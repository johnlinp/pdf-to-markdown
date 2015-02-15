# -*- coding: utf8 -*-

import re


class Syntax(object):
	def __init__(self):
		pass


	def pattern(self):
		return 'plain-text'


	def newline(self):
		return True


class UrbanSyntax(Syntax):
	def __init__(self):
		pass


	def pattern(self, text):
		content = text.get_text().encode('utf8').strip()

		mo = re.search('^(（|\()(一|二|三|四|五|六|七|八|九|十)(）|\))', content)
		if mo:
			return 'heading-2'

		mo = re.search('^\d+、', content)
		if mo:
			return 'ordered-list-item'

		return 'plain-text'

	def newline(self, text):
		content = text.get_text().encode('utf8').strip()
		mo = re.search('。$', content)
		return bool(mo)


	def purify(self, text):
		content = text.get_text().encode('utf8').strip()

		mo = re.match('(（|\()(一|二|三|四|五|六|七|八|九|十)(）|\))(.*)', content)
		if mo:
			return mo.group(4)

		mo = re.match('^\d+、(.*)', content)
		if mo:
			return mo.group(1)

		return content

