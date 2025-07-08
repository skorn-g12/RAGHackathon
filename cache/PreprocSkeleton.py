import os
import pdfplumber
import camelot
import fitz  # Currently unused
from typing import List, Tuple


class PDFExtractor:
  """
  Extracts raw text (excluding table regions) and structured table data
  from a list of PDF files using pdfplumber and Camelot.
  """

  def __init__(self, pdf_paths: List[str]):
    """
    Initialize the extractor with a list of PDF file paths.
    """
    self.pdf_paths = pdf_paths

  def extract_text_and_tables(self) -> Tuple[str, List]:
    """
    Extracts text (excluding tables) and tables from all provided PDFs.

    Returns:
      A tuple:
        - raw_text: A string containing extracted text with delimiters.
        - table_data: A list of pandas DataFrames for each table found.
    """
    raw_text = "<<START>>"
    table_data = []

    # Extract raw text using pdfplumber, excluding detected table regions
    for pdf_path in self.pdf_paths:
      with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
          tables = page.find_tables()
          table_bounds = [t.bbox for t in tables]

          # Filter out text inside table bounding boxes
          text = page.filter(
            lambda obj: not any(
              t[0] <= obj["x0"] <= t[2] and t[1] <= obj["top"] <= t[3]
              for t in table_bounds
            )
          ).extract_text(x_tolerance=1)

          if text:
            raw_text += text + "<<END>>\n<<START>>"

    print("Text extraction done.")

    # Extract tables using Camelot's lattice mode
    for pdf_path in self.pdf_paths:
      tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
      print(f"Found {tables.n} tables in {pdf_path}.")
      for table in tables:
        table_data.append(table.df)

    return raw_text, table_data


class PDFPathFinder:
  """
  Finds all PDF files recursively within a given directory.
  """

  def __init__(self, dir_path: str):
    """
    Initialize with the relative or absolute directory path.
    """
    self.dir_path = dir_path

  def get_pdf_paths(self) -> List[str]:
    """
    Walks through the directory tree and collects all PDF file paths.

    Returns:
      A list of absolute file paths to PDF files.
    """
    pdf_paths = []
    for root, _, files in os.walk(self.dir_path):
      for file in files:
        if file.lower().endswith(".pdf"):
          full_path = os.path.abspath(os.path.join(root, file))
          pdf_paths.append(full_path)
    return pdf_paths


class TextFileWriter:
  """
  Handles writing or appending text to a file.
  """

  def __init__(self, filename: str):
    """
    Initialize with the target filename.
    """
    self.filename = filename

  def write_text(self, text: str):
    """
    Write the given text to the file, overwriting existing content.
    """
    with open(self.filename, 'w', encoding='utf-8') as file:
      file.write(text)

  def append_text(self, text: str):
    """
    Append the given text to the file.
    """
    with open(self.filename, 'a', encoding='utf-8') as file:
      file.write(text)


class Runner:
  """
  Orchestrates the entire PDF extraction pipeline.
  """

  def __init__(self, pdf_dir: str, output_dir: str):
    """
    Initialize the runner with input and output directories.
    """
    self.pdf_dir = pdf_dir
    self.output_dir = output_dir
    self.pdf_paths: List[str] = []
    self.extractor: PDFExtractor = None
    self.text_writer: TextFileWriter = None

  def run(self):
    """
    Executes the full extraction pipeline:
    - Finds PDFs
    - Extracts text and tables
    - Saves text and table data to output directory
    """
    # Step 1: Locate all PDF files
    finder = PDFPathFinder(self.pdf_dir)
    self.pdf_paths = finder.get_pdf_paths()

    if not self.pdf_paths:
      print("No PDF files found.")
      return

    # Step 2: Extract text and tables
    self.extractor = PDFExtractor(self.pdf_paths)
    raw_text, table_data = self.extractor.extract_text_and_tables()

    # Step 3: Save extracted text
    text_path = os.path.join(self.output_dir, "text.txt")
    self.text_writer = TextFileWriter(text_path)
    self.text_writer.write_text(raw_text)

    # Step 4: Save tables as CSVs
    for idx, dataframe in enumerate(table_data, start=1):
      dataframe = dataframe.map(lambda x: x.replace('\n', ' ') if isinstance(x, str) else x)
      table_path = os.path.join(self.output_dir, f"table_{idx}.csv")
      dataframe.to_csv(table_path, index=False)

    print("Extraction and writing completed.")


if __name__ == "__main__":
  # Instantiate and run the pipeline
  runner = Runner(pdf_dir="./../pdf_data", output_dir="./../extracted_text")
  runner.run()
