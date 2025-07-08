import os
from typing import List

class PDFPathFinder:
  """
  Finds all PDF files recursively within a given directory.
  """
  def __init__(self, dir_path: str):
    self.dir_path = dir_path

  def get_pdf_paths(self) -> List[str]:
    pdf_paths = []
    for root, _, files in os.walk(self.dir_path):
      for file in files:
        if file.lower().endswith(".pdf"):
          full_path = os.path.abspath(os.path.join(root, file))
          pdf_paths.append(full_path)
    return pdf_paths
