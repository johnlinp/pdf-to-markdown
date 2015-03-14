class Writer(object):
	def __init__(self):
		self._mode = 'simple'
		self._title = 'markdown'


	def set_syntax(self, syntax):
		self._syntax = syntax


	def set_mode(self, mode):
		self._mode = mode


	def set_title(self, title):
		self._title = title


	def write(self, piles):
		self._write_simple(piles)


	def _write_simple(self, piles):
		filename = self._title + '.md'
		with open(filename, 'w') as fwrite:
			for pile in piles:
				if pile.get_type() == 'image':
					image = pile.get_image()
					self._save_image(image)
				markdown = pile.gen_markdown(self._syntax)
				fwrite.write(markdown)


	def _save_image(self, image):
		result = None
		if not image.stream:
			raise Exception('No stream found')
		stream = image.stream.get_rawdata()
		with open(image.name, 'wb') as fwrite:
			fwrite.write(stream)
			fwrite.close()

