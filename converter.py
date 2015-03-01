from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pile import Pile
from syntax import UrbanSyntax


class Converter(object):
	def __init__(self, filename):
		self._document = self._read_file(filename)
		self._device, self._interpreter = self._prepare_tools()
		self._syntax = UrbanSyntax()
		self._pages = {}


	def parse(self, max_page_num=None):
		for page in PDFPage.create_pages(self._document):
			self._interpreter.process_page(page)
			layout = self._device.get_result()

			if max_page_num != None and layout.pageid > max_page_num:
				break

			self._pages[layout.pageid] = layout


	def convert(self, page_num=None):
		if page_num == None:
			for page in self._pages:
				self._convert_page(page)
		else:
			page = self._pages[page_num]
			self._convert_page(page)


	def _read_file(self, filename):
		parser = PDFParser(open(filename, 'rb'))
		document = PDFDocument(parser)
		return document


	def _prepare_tools(self):
		laparams = LAParams()
		rsrcmgr = PDFResourceManager()
		device = PDFPageAggregator(rsrcmgr, laparams=laparams)
		interpreter = PDFPageInterpreter(rsrcmgr, device)

		return device, interpreter


	def _convert_page(self, page):
		pile = Pile()
		pile.parse_page(page)
		piles = pile.split_piles()

		#print 'len(piles):', len(piles)

		for idx, pile in enumerate(piles):
			filename = 'part{}.html'.format(idx)
			string = pile.gen_html()
			with open(filename, 'w') as fw:
				fw.write(string)

			filename = 'part{}.md'.format(idx)
			string = pile.gen_markdown(self._syntax)
			with open(filename, 'w') as fw:
				fw.write(string)

