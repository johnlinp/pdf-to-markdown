from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.layout import LTFigure
from pdfminer.layout import LTTextBox
from pdfminer.layout import LTTextLine
from pdfminer.layout import LTTextBoxHorizontal
from pdfminer.layout import LTTextLineHorizontal
from pdfminer.layout import LTLine
from pdfminer.layout import LTRect
from pdfminer.layout import LTImage
from pdfminer.layout import LTCurve
from pdfminer.converter import PDFPageAggregator


def parse(layout):
	x_set, y_set = set(), set()
	lines = []
	objstack = list(reversed(list(layout)))
	while objstack:
		b = objstack.pop()
		if type(b) in [LTFigure, LTTextBox, LTTextLine, LTTextBoxHorizontal]:
			objstack.extend(reversed(list(b)))
		elif type(b) == LTTextLineHorizontal:
			lines.append(b)
		elif type(b) == LTRect:
			if b.x1 - b.x0 < 2.0:
				x_set.add(b.y0)
			else:
				y_set.add(b.x0)
		elif type(b) == LTImage:
			pass
		elif type(b) == LTCurve:
			pass
		else:
			assert False, "Unrecognized type: %s" % type(b)

	return x_set, y_set, lines


def layout():
	target_page = 13

	fp = open('neihu.pdf', 'rb')
	parser = PDFParser(fp)
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
		all_x_set, all_y_set = set(), set()
		all_lines = []
		for element in layout:
			one_x_set, one_y_set, one_lines = parse(layout)
			all_x_set = all_x_set | one_x_set
			all_y_set = all_y_set | one_y_set
			all_lines.extend(one_lines)

		all_x_list = sorted(list(all_x_set))
		all_y_list = sorted(list(all_y_set))

		division = '================================================='

		print division
		print 'all lines'
		print division
		for line in all_lines:
			print line.x0, line.x1, line.y0, line.y1
			print line.get_text().encode('utf8')
			print division

		print 'all x'
		print division
		for x in all_x_list:
			print x
		print division

		print 'all y'
		print division
		for y in all_y_list:
			print y
		print division


if __name__ == '__main__':
	layout()

