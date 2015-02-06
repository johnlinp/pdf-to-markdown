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
	vertical, horizontal = [], []
	lines = []

	objstack = list(reversed(list(layout)))
	while objstack:
		b = objstack.pop()
		if type(b) in [LTFigure, LTTextBox, LTTextLine, LTTextBoxHorizontal]:
			objstack.extend(reversed(list(b)))
		elif type(b) == LTTextLineHorizontal:
			lines.append(b)
		elif type(b) == LTRect:
			if b.x1 - b.x0 < 1.0:
				vertical.append((b.x0, b.y0, b.y1))
			elif b.y1 - b.y0 < 1.0:
				horizontal.append((b.y0, b.x0, b.x1))
			elif 15.0 < b.y1 - b.y0 < 18.0: # grey blocks
				pass
			else:
				raise Exception('strange lines')
		elif type(b) == LTImage:
			pass
		elif type(b) == LTCurve:
			pass
		else:
			assert False, "Unrecognized type: %s" % type(b)

	vertical = sorted(vertical, reverse=True)
	horizontal = sorted(horizontal, reverse=True)

	return vertical, horizontal, lines


def layout():
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

		vertical, horizontal, lines = parse(layout)

		print len(vertical), len(horizontal), len(lines)

		division = '================================================='

		print division
		print 'all lines'
		print division
		for line in lines:
			print 'x: from {} to {}'.format(line.x0, line.x1)
			print 'y: from {} to {}'.format(line.y0, line.y1)
			print line.get_text().encode('utf8')
			print division

		print 'all vertical'
		print division
		for vertical in vertical:
			print 'x: {}, y: from {} to {}'.format(vertical[0], vertical[1], vertical[2])
		print division

		print 'all horizontal'
		print division
		for horizontal in horizontal:
			print 'y: {}, x: from {} to {}'.format(horizontal[0], horizontal[1], horizontal[2])
		print division


if __name__ == '__main__':
	layout()

