class Writer(object):
	def __init__(self):
		self._mode = 'simple'

	def set_mode(self, mode):
		self._mode = mode

	def set_title(self, title):
		self._title = title

	def write(self, markdown):
		filename = self._title + '.md'
		with open(filename, 'w') as fwrite:
			fwrite.write(markdown)
