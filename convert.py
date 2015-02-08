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


def is_overlap(top, bottom, obj):
	return (bottom - 1.0) <= obj.y0 <= (top + 1.0) or \
		   (bottom - 1.0) <= obj.y1 <= (top + 1.0)


def calc_top_bottom(objects):
	top = float('-inf')
	bottom = float('inf')
	for obj in objects:
		top = max(top, obj.y1)
		bottom = min(bottom, obj.y0)
	return top, bottom


def find_near_verticals(start, verticals):
	near_verticals = [start]
	top = start.y1
	bottom = start.y0
	for vertical in verticals:
		if vertical == start:
			continue
		if is_overlap(top, bottom, vertical):
			near_verticals.append(vertical)
			top, bottom = calc_top_bottom(near_verticals)
	return near_verticals


def find_included(top, bottom, objects):
	included = []
	for obj in objects:
		if is_overlap(top, bottom, obj):
			included.append(obj)
	return included


def find_tables(verticals, horizontals, lines):
	tables = []
	visited = set()
	for vertical in verticals:
		if vertical in visited:
			continue

		near_verticals = find_near_verticals(vertical, verticals)
		top, bottom = calc_top_bottom(near_verticals)
		included_horizontals = find_included(top, bottom, horizontals)
		included_lines = find_included(top, bottom, lines)

		table = {
			'verticals': near_verticals,
			'horizontals': included_horizontals,
			'lines': included_lines,
		}

		tables.append(table)
		visited.update(near_verticals)
	return tables


def find_paragraphs(lines, tables):
	tops = []
	for table in tables:
		verticals = table['verticals']
		top, bottom = calc_top_bottom(verticals)
		tops.append(top)

	all_table_lines = set()
	for table in tables:
		table_lines = table['lines']
		all_table_lines.update(table_lines)

	num_slots = len(tables) + 1
	paragraphs = [[] for idx in range(num_slots)]
	for line in lines:
		if line in all_table_lines:
			continue
		for idx, table in enumerate(tables):
			if line.y0 > tops[idx]:
				paragraphs[idx].append(line)
				break

	paragraphs = filter(None, paragraphs)
	paragraphs = [{'lines': paragraph, 'verticals': [], 'horizontals': []} for paragraph in paragraphs]

	return paragraphs


def find_groups(verticals, horizontals, lines):
	groups = []

	tables = find_tables(verticals, horizontals, lines)
	paragraphs = find_paragraphs(lines, tables)

	groups = sorted(tables + paragraphs, reverse=True, key=lambda x: x['lines'][0].y0)

	return groups


def gen_html(filename, verticals, horizontals, lines):
	fw = open(filename, 'w')

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

	for vertical in verticals:
		info = {
			'width': 1,
			'height': vertical.y1 - vertical.y0,
			'x': vertical.x0,
			'y': vertical.y0,
			'text': '',
			'fill': 'blue',
		}
		fw.write(rect.format(**info))

	for horizontal in horizontals:
		info = {
			'width': horizontal.x1 - horizontal.x0,
			'height': 1,
			'x': horizontal.x0,
			'y': horizontal.y0,
			'text': '',
			'fill': 'red',
		}
		fw.write(rect.format(**info))

	fw.write('</g>')
	fw.write('</svg>')


def parse_page(layout):
	verticals, horizontals = [], []
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
				verticals.append(b)
			elif b.y1 - b.y0 < 1.0:
				horizontals.append(b)
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

	return verticals, horizontals, lines


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

		verticals, horizontals, lines = parse_page(layout)
		groups = find_groups(verticals, horizontals, lines)

		for idx, group in enumerate(groups):
			gen_html('part{}.html'.format(idx), group['verticals'], group['horizontals'], group['lines'])



if __name__ == '__main__':
	main()

