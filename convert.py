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


def main():
	target_page = 13

	parser = PDFParser(open('neihu.pdf', 'rb'))
	document = PDFDocument(parser)
	laparams = LAParams()
	rsrcmgr = PDFResourceManager()
	device = PDFPageAggregator(rsrcmgr, laparams=laparams)
	interpreter = PDFPageInterpreter(rsrcmgr, device)

	for page in PDFPage.create_pages(document):
		interpreter.process_page(page)
		layout = device.get_result()

		if layout.pageid < target_page:
			continue
		elif layout.pageid > target_page:
			break

		print 'layout.pageid:', layout.pageid

		syntax = UrbanSyntax()
		pile = Pile()
		pile.parse_page(layout)
		piles = pile.split_piles()

		print 'len(piles):', len(piles)

		for idx, pile in enumerate(piles):
			filename = 'part{}.html'.format(idx)
			string = pile.gen_html()
			with open(filename, 'w') as fw:
				fw.write(string)

			filename = 'part{}.md'.format(idx)
			string = pile.gen_markdown(syntax)
			with open(filename, 'w') as fw:
				fw.write(string)


if __name__ == '__main__':
	main()

