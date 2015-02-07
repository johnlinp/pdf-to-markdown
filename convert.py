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


def html(vertical, horizontal, lines):
	fw = open('page.html', 'w')

	page_height = 800 # for flipping the coordinate

	fw.write('<meta charset="utf8" />')
	fw.write('<svg width="100%" height="100%">')

	# flip coordinate
	fw.write('<g transform="translate(0, {}) scale(1, -1)">'.format(page_height))

	rect = '<rect width="{width}" height="{height}" x="{x}" y="{y}" fill="{fill}"><title>{text}</title></rect>'

	for line in lines:
		info = {
			'width': line.x1 - line.x0,
			'height': line.y1 - line.y0,
			'x': line.x0,
			'y': line.y0,
			'text': line.get_text().encode('utf8'),
			'fill': 'green',
		}
		fw.write(rect.format(**info))

	for vertical in vertical:
		info = {
			'width': 1,
			'height': vertical[2] - vertical[1],
			'x': vertical[0],
			'y': vertical[1],
			'text': '',
			'fill': 'blue',
		}
		fw.write(rect.format(**info))

	for horizontal in horizontal:
		info = {
			'width': horizontal[2] - horizontal[1],
			'height': 1,
			'x': horizontal[1],
			'y': horizontal[0],
			'text': '',
			'fill': 'red',
		}
		fw.write(rect.format(**info))

	fw.write('</g>')
	fw.write('</svg>')


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
		html(vertical, horizontal, lines)



if __name__ == '__main__':
	layout()

