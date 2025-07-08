class TextFileWriter:
  """
  Handles writing or appending text to a file.
  """
  def __init__(self, filename: str):
    self.filename = filename

  def write_text(self, text: str):
    with open(self.filename, 'w', encoding='utf-8') as file:
      file.write(text)

  def append_text(self, text: str):
    with open(self.filename, 'a', encoding='utf-8') as file:
      file.write(text)
