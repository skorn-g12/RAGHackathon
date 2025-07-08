import pdfplumber
import camelot
from typing import List, Tuple

class PDFExtractor:
  """
  Extracts raw text (excluding table regions) and structured table data
  from a list of PDF files using pdfplumber and Camelot.
  """
  def __init__(self, pdf_paths: List[str]):
    self.pdf_paths = pdf_paths

  def extract_text_and_tables(self) -> Tuple[str, List]:
    raw_text = "<<START>>"
    table_data = []

    for pdf_path in self.pdf_paths:
      with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
          tables = page.find_tables()
          table_bounds = [t.bbox for t in tables]
          text = page.filter(
            lambda obj: not any(
              t[0] <= obj["x0"] <= t[2] and t[1] <= obj["top"] <= t[3]
              for t in table_bounds
            )
          ).extract_text(x_tolerance=1)

          if text:
            raw_text += text + "<<END>>\n<<START>>"

    print("Text extraction done.")

    for pdf_path in self.pdf_paths:
      tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
      print(f"Found {tables.n} tables in {pdf_path}.")
      for table in tables:
        table_data.append(table.df)

    return raw_text, table_data
