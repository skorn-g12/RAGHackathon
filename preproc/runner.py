import os
from typing import List
from .pdf_path_finder import PDFPathFinder
from .pdf_extractor import PDFExtractor
from .text_writer import TextFileWriter

class Runner:
  """
  Orchestrates the entire PDF extraction pipeline.
  """
  def __init__(self, pdf_dir: str, output_dir: str):
    self.pdf_dir = pdf_dir
    self.output_dir = output_dir
    self.pdf_paths: List[str] = []
    self.extractor: PDFExtractor = None
    self.text_writer: TextFileWriter = None

  def run(self):
    finder = PDFPathFinder(self.pdf_dir)
    self.pdf_paths = finder.get_pdf_paths()

    if not self.pdf_paths:
      print("No PDF files found.")
      return

    self.extractor = PDFExtractor(self.pdf_paths)
    raw_text, table_data = self.extractor.extract_text_and_tables()

    text_path = os.path.join(self.output_dir, "text.txt")
    self.text_writer = TextFileWriter(text_path)
    self.text_writer.write_text(raw_text)

    for idx, dataframe in enumerate(table_data, start=1):
      dataframe = dataframe.map(lambda x: x.replace('\n', ' ') if isinstance(x, str) else x)
      table_path = os.path.join(self.output_dir, f"table_{idx}.csv")
      dataframe.to_csv(table_path, index=False)

    print("Extraction and writing completed.")
