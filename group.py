class Group(object):
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
