# -*- coding: utf8 -*-

import pdb
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

		if not content:
			return 'none'

		if content.isdigit(): # page number
			return 'none'

		if 17.9 < text.height < 18.1:
			return 'heading-3'

		if 20.0 < text.height < 20.1:
			return 'heading-1'

		if 15.9 < text.height < 16.0:
			return 'heading-2'

		mo = re.search('^(一|二|三|四|五|六|七|八|九|十)、', content)
		if mo:
			return 'heading-3'

		mo = re.search('^(（|\()(一|二|三|四|五|六|七|八|九|十)(）|\))', content)
		if mo:
			return 'heading-4'

		mo = re.search('^\d+、', content)
		if mo:
			return 'ordered-list-item'

		if text.x0 < 90.1: # special case for neihu page 2
			return 'unordered-list-item'

		return 'plain-text'

	def newline(self, text):
		content = text.get_text().encode('utf8').strip()

		if text.x0 < 90.1: # special case for neihu page 2
			return True

		mo = re.search('。$', content)
		if mo:
			return True

		if text.x1 > 505.0: # reach the right margin
			return False

		return True


	def purify(self, text):
		content = text.get_text().encode('utf8').strip()

		mo = re.match('(一|二|三|四|五|六|七|八|九|十)、(.*)', content)
		if mo:
			return mo.group(2)

		mo = re.match('(（|\()(一|二|三|四|五|六|七|八|九|十)(）|\))(.*)', content)
		if mo:
			return mo.group(4)

		mo = re.match('^\d+、(.*)', content)
		if mo:
			return mo.group(1)

		return content

