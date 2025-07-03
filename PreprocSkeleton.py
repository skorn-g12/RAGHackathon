import pdfplumber
import camelot
import fitz
import os
class PDFExtractor:
	def __init__(self,pdf_path):
		self.pdf_path =pdf_path
	def extrac_text_and_tables(self):
		raw_text="<<START>>";
		table_data=[]
		for pdf_path in self.pdf_path:
			with pdfplumber.open(pdf_path) as pdf:
				for page in pdf.pages:
					tables =page.find_tables()
					table_bounds =[t.bbox for t in tables]
					text=page.filter(lambda obj: not any(t[0] <= obj["x0"]<=t[2] and t[1]<=obj["top"]<=t[3] for t in table_bounds)).extract_text(x_tolerance=1)
					#print(f"page num:{page}", table_bounds)
					raw_text+= text + "<<END>>\n" + "<<START>>"
		print("text extraction done")
		#Use Camelot for table extraction 
		for pdf_path in self.pdf_path:
			tables =camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
			print(f"Found {tables.n} tables.")
			for table in tables:
				table_data.append(table.df)

		return raw_text, table_data
class getPDFpath:
	def __init__(self,dir_path):
		self.dir_path_relative =dir_path
	def get_pdf_paths(self):
		pdf_paths=[]
		for root,_,files in os.walk(self.dir_path_relative):
			for file in files:
				if file.lower().endswith(".pdf"):
					full_path = os.path.abspath(os.path.join(root, file))
					pdf_paths.append(full_path)
		return pdf_paths

class TextFileWriter:
    def __init__(self, filename):
        self.filename = filename

    def write_text(self, text):
        with open(self.filename, 'w', encoding='utf-8') as file:
            file.write(text)

    def append_text(self, text):
        with open(self.filename, 'a', encoding='utf-8') as file:
            file.write(text)

if __name__ == "__main__":
	pdfs= getPDFpath("./../pdf_data")
	pdf_path_list= pdfs.get_pdf_paths()
	extractor= PDFExtractor(pdf_path_list)
	raw_text, table_data = extractor.extrac_text_and_tables()
	textfile = TextFileWriter("./../extracted_text/text.txt")
	textfile.write_text(raw_text)
	#table data is pandas datatframe. store it as a CSV  for time being 
	for count,dataframe in enumerate(table_data,start=1):
		dataframe = dataframe.map(lambda x: x.replace('\n', ' ') if isinstance(x, str) else x)
		dataframe.to_csv(f"./../extracted_text/table_{count}",index=False)
	#table_data= TextFileWriter("./../extracted_text/table.txt")
	#textfile.write_text(table_data)
