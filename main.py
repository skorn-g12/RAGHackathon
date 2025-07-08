from extractor.runner import Runner

if __name__ == "__main__":
  runner = Runner(pdf_dir="./../pdf_data", output_dir="./../extracted_text")
  runner.run()
