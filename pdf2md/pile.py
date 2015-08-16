from pdfminer.layout import LTFigure
from pdfminer.layout import LTTextBox
from pdfminer.layout import LTTextLine
from pdfminer.layout import LTTextBoxHorizontal
from pdfminer.layout import LTTextLineHorizontal
from pdfminer.layout import LTLine
from pdfminer.layout import LTRect
from pdfminer.layout import LTImage
from pdfminer.layout import LTCurve
from pdfminer.layout import LTChar
from pdfminer.layout import LTLine
import binascii

class Pile(object):
	def __init__(self):
		self.verticals = []
		self.horizontals = []
		self.texts = []
		self.images = []

		self._SEARCH_DISTANCE = 1.0

	def __nonzero__(self):
		return bool(self.texts)

	def get_type(self):
		if self.verticals:
			return 'table'
		elif self.images:
			return 'image'
		else:
			return 'paragraph'

	def parse_layout(self, layout):
		obj_stack = list(reversed(list(layout)))
		while obj_stack:
			obj = obj_stack.pop()
			if type(obj) in [LTFigure, LTTextBox, LTTextLine, LTTextBoxHorizontal]:
				obj_stack.extend(reversed(list(obj)))
			elif type(obj) == LTTextLineHorizontal:
				self.texts.append(obj)
			elif type(obj) == LTRect:
				if obj.width < 1.0:
					self._adjust_to_close(obj, self.verticals, 'x0')
					self.verticals.append(obj)
				elif obj.height < 1.0:
					self._adjust_to_close(obj, self.horizontals, 'y0')
					self.horizontals.append(obj)
			elif type(obj) == LTImage:
				self.images.append(obj)
			elif type(obj) == LTCurve:
				pass
			elif type(obj) == LTChar:
				pass
			elif type(obj) == LTLine:
				pass					
			else:
				assert False, "Unrecognized type: %s" % type(obj)


	def split_piles(self):
		tables = self._find_tables()
		paragraphs = self._find_paragraphs(tables)
		images = self._find_images()

		piles = sorted(tables + paragraphs + images, reverse=True, key=lambda x: x._get_anything().y0)

		return piles


	def gen_markdown(self, syntax):
		pile_type = self.get_type()
		if pile_type == 'paragraph':
			return self._gen_paragraph_markdown(syntax)
		elif pile_type == 'table':
			return self._gen_table_markdown(syntax)
		elif pile_type == 'image':
			return self._gen_image_markdown()
		else:
			raise Exception('Unsupported markdown type')


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


	def get_image(self):
		if not self.images:
			raise Exception('No images here')
		return self.images[0]


	def _adjust_to_close(self, obj, lines, attr):
		obj_coor = getattr(obj, attr)
		close = None
		for line in lines:
			line_coor = getattr(line, attr)
			if abs(obj_coor - line_coor) < self._SEARCH_DISTANCE:
				close = line
				break

		if not close:
			return

		if attr == 'x0':
			new_bbox = (close.bbox[0], obj.bbox[1], close.bbox[2], obj.bbox[3])
		elif attr == 'y0':
			new_bbox = (obj.bbox[0], close.bbox[1], obj.bbox[2], close.bbox[3])
		else:
			raise Exception('No such attr')
		obj.set_bbox(new_bbox)

	def _find_tables(self):
		tables = []
		visited = set()
		for vertical in self.verticals:
			if vertical in visited:
				continue

			near_verticals = self._find_near_verticals(vertical, self.verticals)
			top, bottom = self._calc_top_bottom(near_verticals)
			included_horizontals = self._find_included(top, bottom, self.horizontals)
			included_texts = self._find_included(top, bottom, self.texts)

			table = Pile()
			table.verticals = near_verticals
			table.horizontals = included_horizontals
			table.texts = included_texts

			tables.append(table)
			visited.update(near_verticals)
		return tables


	def _find_paragraphs(self, tables):
		tops = []
		for table in tables:
			top, bottom = self._calc_top_bottom(table.verticals)
			tops.append(top)

		tops.append(float('-inf')) # for the last part of paragraph

		all_table_texts = set()
		for table in tables:
			all_table_texts.update(table.texts)

		num_slots = len(tables) + 1
		paragraphs = [Pile() for idx in range(num_slots)]
		for text in self.texts:
			if text in all_table_texts:
				continue
			for idx, top in enumerate(tops):
				if text.y0 > top:
					paragraphs[idx].texts.append(text)
					break

		paragraphs = filter(None, paragraphs)

		return paragraphs


	def _find_images(self):
		images = []
		for image in self.images:
			pile = Pile()
			pile.images.append(image)
			images.append(pile)
		return images


	def _get_anything(self):
		if self.texts:
			return self.texts[0]
		if self.images:
			return self.images[0]
		raise Exception('The pile contains nothing')


	def _is_overlap(self, top, bottom, obj):
		assert top > bottom
		return (bottom - self._SEARCH_DISTANCE) <= obj.y0 <= (top + self._SEARCH_DISTANCE) or \
			   (bottom - self._SEARCH_DISTANCE) <= obj.y1 <= (top + self._SEARCH_DISTANCE)


	def _calc_top_bottom(self, objects):
		top = float('-inf')
		bottom = float('inf')
		for obj in objects:
			top = max(top, obj.y1)
			bottom = min(bottom, obj.y0)
		return top, bottom


	def _find_near_verticals(self, start, verticals):
		near_verticals = [start]
		top = start.y1
		bottom = start.y0
		for vertical in verticals:
			if vertical == start:
				continue
			if self._is_overlap(top, bottom, vertical):
				near_verticals.append(vertical)
				top, bottom = self._calc_top_bottom(near_verticals)
		return near_verticals


	def _find_included(self, top, bottom, objects):
		included = []
		for obj in objects:
			if self._is_overlap(top, bottom, obj):
				included.append(obj)
		return included


	def _gen_paragraph_markdown(self, syntax):
		markdown = ''
		for text in self.texts:
			pattern = syntax.pattern(text)
			newline = syntax.newline(text)
			content = syntax.purify(text)

			if pattern == 'none':
				continue
			elif pattern.startswith('heading'):
				lead = '#' * int(pattern[-1])
				markdown += lead + ' ' + content
			elif pattern.startswith('plain-text'):
				markdown += content
			elif pattern.endswith('list-item'):
				lead = '1.' if pattern.startswith('ordered') else '-'
				markdown += lead + ' ' + content
			else:
				raise Exception('Unsupported syntax pattern')

			if newline:
				markdown += '\n\n'

		return markdown


	def _gen_table_markdown(self, syntax):
		intermediate = self._gen_table_intermediate()
		return self._intermediate_to_markdown(intermediate)


	def _gen_image_markdown(self):
		image = self.get_image()
		return '![{0}](images/{0})\n\n'.format(image.name)


	def _gen_table_intermediate(self):
		vertical_coor = self._calc_coordinates(self.verticals, 'x0', False)
		horizontal_coor = self._calc_coordinates(self.horizontals, 'y0', True)
		num_rows = len(horizontal_coor) - 1
		num_cols = len(vertical_coor) - 1

		intermediate = [[] for idx in range(num_rows)]
		for row_idx in range(num_rows):
			for col_idx in range(num_cols):
				left = vertical_coor[col_idx]
				top = horizontal_coor[row_idx]
				right = vertical_coor[col_idx + 1]
				bottom = horizontal_coor[row_idx + 1]

				assert top > bottom

				if self._is_ignore_cell(left, top, right, bottom):
					continue

				right, colspan = self._find_exist_coor(bottom, top, col_idx, vertical_coor, 'vertical')
				bottom, rowspan = self._find_exist_coor(left, right, row_idx, horizontal_coor, 'horizontal')

				cell = {}
				cell['texts'] = self._find_cell_texts(left, top, right, bottom)
				if colspan > 1:
					cell['colspan'] = colspan
				if rowspan > 1:
					cell['rowspan'] = rowspan

				intermediate[row_idx].append(cell)

		return intermediate


	def _find_cell_texts(self, left, top, right, bottom):
		texts = []
		for text in self.texts:
			if self._in_range(left, top, right, bottom, text):
				texts.append(text)
		return texts


	def _in_range(self, left, top, right, bottom, obj):
		return (left - self._SEARCH_DISTANCE) <= obj.x0 < obj.x1 <= (right + self._SEARCH_DISTANCE) and \
			   (bottom - self._SEARCH_DISTANCE) <= obj.y0 < obj.y1 <= (top + self._SEARCH_DISTANCE)


	def _is_ignore_cell(self, left, top, right, bottom):
		left_exist = self._line_exists(left, bottom, top, 'vertical')
		top_exist = self._line_exists(top, left, right, 'horizontal')
		return not left_exist or not top_exist


	def _find_exist_coor(self, minimum, maximum, start_idx, line_coor, direction):
		span = 0
		line_exist = False
		while not line_exist:
			span += 1
			coor = line_coor[start_idx + span]
			line_exist = self._line_exists(coor, minimum, maximum, direction)
		return coor, span


	def _line_exists(self, target, minimum, maximum, direction):
		if direction == 'vertical':
			lines = self.verticals
			attr = 'x0'
			fill_range = self._fill_vertical_range
		elif direction == 'horizontal':
			lines = self.horizontals
			attr = 'y0'
			fill_range = self._fill_horizontal_range
		else:
			raise Exception('No such direction')

		for line in lines:
			if getattr(line, attr) != target:
				continue
			if fill_range(minimum, maximum, line):
				return True

		return False


	def _fill_vertical_range(self, bottom, top, obj):
		assert top > bottom
		return obj.y0 <= (bottom + self._SEARCH_DISTANCE) and (top - self._SEARCH_DISTANCE) <= obj.y1


	def _fill_horizontal_range(self, left, right, obj):
		return obj.x0 <= (left + self._SEARCH_DISTANCE) and (right - self._SEARCH_DISTANCE) <= obj.x1


	def _intermediate_to_markdown(self, intermediate):
		markdown = ''
		markdown += self._create_tag('table', True, 0)
		for row in intermediate:
			markdown += self._create_tag('tr', True, 1)
			for cell in row:
				markdown += self._create_td_tag(cell)
			markdown += self._create_tag('tr', False, 1)
		markdown += self._create_tag('table', False, 0)
		markdown += '\n'
		return markdown


	def _create_tag(self, tag_name, start, level):
		indent = '\t' * level
		slash = '' if start else '/'
		center = ' align="center"' if start else ''
		return indent + '<' + slash + tag_name + center + '>\n'


	def _create_td_tag(self, cell):
		indent = '\t' * 2
		texts = [text.get_text().encode('utf8').strip() for text in cell['texts']]
		texts = ' '.join(texts)
		colspan = ' colspan={}'.format(cell['colspan']) if 'colspan' in cell else ''
		rowspan = ' rowspan={}'.format(cell['rowspan']) if 'rowspan' in cell else ''
		return indent + '<td' + colspan + rowspan + '>' + texts + '</td>\n'


	def _calc_coordinates(self, axes, attr, reverse):
		coor_set = set()
		for axis in axes:
			coor_set.add(getattr(axis, attr))
		coor_list = list(coor_set)
		coor_list.sort(reverse=reverse)
		return coor_list


