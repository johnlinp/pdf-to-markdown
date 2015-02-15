from pdfminer.layout import LTFigure
from pdfminer.layout import LTTextBox
from pdfminer.layout import LTTextLine
from pdfminer.layout import LTTextBoxHorizontal
from pdfminer.layout import LTTextLineHorizontal
from pdfminer.layout import LTLine
from pdfminer.layout import LTRect
from pdfminer.layout import LTImage
from pdfminer.layout import LTCurve

class Pile(object):
	def __init__(self):
		self.verticals = []
		self.horizontals = []
		self.texts = []

	def __nonzero__(self):
		return bool(self.texts)

	def get_type(self):
		if self.verticals:
			return 'table'
		else:
			return 'paragraph'

	def parse_page(self, layout):
		objstack = list(reversed(list(layout)))
		while objstack:
			b = objstack.pop()
			if type(b) in [LTFigure, LTTextBox, LTTextLine, LTTextBoxHorizontal]:
				objstack.extend(reversed(list(b)))
			elif type(b) == LTTextLineHorizontal:
				self.texts.append(b)
			elif type(b) == LTRect:
				if b.x1 - b.x0 < 1.0:
					self.verticals.append(b)
				elif b.y1 - b.y0 < 1.0:
					self.horizontals.append(b)
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


	def split_piles(self):
		tables = self.find_tables()
		paragraphs = self.find_paragraphs(tables)

		piles = sorted(tables + paragraphs, reverse=True, key=lambda x: x.texts[0].y0)

		return piles


	def gen_markdown(self):
		pile_type = self.get_type()
		if pile_type == 'paragraph':
			return self.gen_paragraph_markdown()
		elif pile_type == 'table':
			return self.gen_table_markdown()
		else:
			raise Exception('unsupported markdown type')


	def gen_html(self):
		html = ''

		page_height = 800 # for flipping the coordinate

		html += '<meta charset="utf8" />'
		html += '<svg width="100%" height="100%">'

		# flip coordinate
		html += '<g transform="translate(0, {}) scale(1, -1)">'.format(page_height)

		rect = '<rect width="{width}" height="{height}" x="{x}" y="{y}" fill="{fill}"><title>{text}</title></rect>'

		for text in self.texts:
			info = {
				'width': text.x1 - text.x0,
				'height': text.y1 - text.y0,
				'x': text.x0,
				'y': text.y0,
				'text': text.get_text().encode('utf8'),
				'fill': 'green',
			}
			html += rect.format(**info)

		for vertical in self.verticals:
			info = {
				'width': 1,
				'height': vertical.y1 - vertical.y0,
				'x': vertical.x0,
				'y': vertical.y0,
				'text': '',
				'fill': 'blue',
			}
			html += rect.format(**info)

		for horizontal in self.horizontals:
			info = {
				'width': horizontal.x1 - horizontal.x0,
				'height': 1,
				'x': horizontal.x0,
				'y': horizontal.y0,
				'text': '',
				'fill': 'red',
			}
			html += rect.format(**info)

		html += '</g>'
		html += '</svg>'

		return html


	def find_tables(self):
		tables = []
		visited = set()
		for vertical in self.verticals:
			if vertical in visited:
				continue

			near_verticals = self.find_near_verticals(vertical, self.verticals)
			top, bottom = self.calc_top_bottom(near_verticals)
			included_horizontals = self.find_included(top, bottom, self.horizontals)
			included_texts = self.find_included(top, bottom, self.texts)

			table = Pile()
			table.verticals = near_verticals
			table.horizontals = included_horizontals
			table.texts = included_texts

			tables.append(table)
			visited.update(near_verticals)
		return tables


	def find_paragraphs(self, tables):
		tops = []
		for table in tables:
			top, bottom = self.calc_top_bottom(table.verticals)
			tops.append(top)

		all_table_texts = set()
		for table in tables:
			all_table_texts.update(table.texts)

		num_slots = len(tables) + 1
		paragraphs = [Pile() for idx in range(num_slots)]
		for text in self.texts:
			if text in all_table_texts:
				continue
			for idx, table in enumerate(tables):
				if text.y0 > tops[idx]:
					paragraphs[idx].texts.append(text)
					break

		paragraphs = filter(None, paragraphs)

		return paragraphs


	def is_overlap(self, top, bottom, obj):
		return (bottom - 1.0) <= obj.y0 <= (top + 1.0) or \
			   (bottom - 1.0) <= obj.y1 <= (top + 1.0)


	def calc_top_bottom(self, objects):
		top = float('-inf')
		bottom = float('inf')
		for obj in objects:
			top = max(top, obj.y1)
			bottom = min(bottom, obj.y0)
		return top, bottom


	def find_near_verticals(self, start, verticals):
		near_verticals = [start]
		top = start.y1
		bottom = start.y0
		for vertical in verticals:
			if vertical == start:
				continue
			if self.is_overlap(top, bottom, vertical):
				near_verticals.append(vertical)
				top, bottom = self.calc_top_bottom(near_verticals)
		return near_verticals


	def find_included(self, top, bottom, objects):
		included = []
		for obj in objects:
			if self.is_overlap(top, bottom, obj):
				included.append(obj)
		return included


	def gen_paragraph_markdown(self):
		markdown = ''
		for text in self.texts:
			content = text.get_text().encode('utf8').strip()
			markdown += content + '\n\n'
		return markdown


	def gen_table_markdown(self):
		return ''


