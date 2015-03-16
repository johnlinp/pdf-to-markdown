# -*- coding: utf8 -*-

import os
import re
import pdb

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
		if self._mode == 'simple':
			self._write_simple(piles)
		elif self._mode == 'gitbook':
			self._write_gitbook(piles)
		else:
			raise Exception('Unsupported mode: ' + self._mode)


	def get_location(self):
		if self._mode == 'simple':
			return self._title + '.md'
		elif self._mode == 'gitbook':
			return self._title
		else:
			raise Exception('Unsupported mode: ' + self._mode)


	def _write_simple(self, piles):
		filename = self._title + '.md'
		with open(filename, 'w') as fwrite:
			for pile in piles:
				if pile.get_type() == 'image':
					image = pile.get_image()
					self._save_image(image, 'images')
				markdown = pile.gen_markdown(self._syntax)
				fwrite.write(markdown)


	def _write_gitbook(self, piles):
		intermediate = self._gen_gitbook_intermediate(piles)
		self._write_gitbook_from_intermediate(intermediate)


	def _gen_gitbook_intermediate(self, piles):
		intermediate = {}

		content = None
		for pile in piles:
			markdown = pile.gen_markdown(self._syntax)
			lines = markdown.split('\n')
			for line in lines:
				mo = re.search('^# (.*)', line)
				if mo and 'title' not in intermediate:
					intermediate['title'] = mo.group(1)
					intermediate['readme'] = []
					intermediate['chapters'] = []
					content = intermediate['readme']

				mo = re.search('^## (.*)', line)
				if mo and 'title' in intermediate:
					chapter = {}
					chapter['title'] = mo.group(1)
					chapter['readme'] = []
					chapter['sections'] = []
					intermediate['chapters'].append(chapter)
					content = chapter['readme']

				mo = re.search('^### (.*)', line)
				if mo and 'title' in intermediate:
					section = {}
					section['title'] = mo.group(1)
					section['content'] = []
					intermediate['chapters'][-1]['sections'].append(section)
					content = section['content']

				if content == None:
					continue

				content.append(line)

		return intermediate


	def _mkdir_anyway(self, dirname):
		if not os.path.exists(dirname):
			os.makedirs(dirname)


	def _write_gitbook_from_intermediate(self, intermediate):
		book_dirname = self._title
		self._mkdir_anyway(book_dirname)
		self._write_gitbook_summary(book_dirname, intermediate)
		self._write_gitbook_content(book_dirname, intermediate)


	def _write_gitbook_summary(self, book_dirname, intermediate):
		lines = []
		line = '* [{}](README.md)'.format(intermediate['title'])
		lines.append(line)
		chapters = intermediate['chapters']
		for idx, chapter in enumerate(chapters):
			line = '* [{}](chapter-{}/README.md)'.format(chapter['title'], idx)
			lines.append(line)
			sections = chapter['sections']
			for jdx, section in enumerate(sections):
				line = '\t* [{}](chapter-{}/section-{}.md)'.format(section['title'], idx, jdx)
				lines.append(line)

		self._write_gitbook_file(os.path.join(book_dirname, 'SUMMARY.md'), lines)


	def _write_gitbook_content(self, book_dirname, intermediate):
		self._write_gitbook_file(os.path.join(book_dirname, 'README.md'), intermediate['readme'])

		chapters = intermediate['chapters']
		for idx, chapter in enumerate(chapters):
			chapter_dirname = os.path.join(book_dirname, 'chapter-{}'.format(idx))
			self._mkdir_anyway(chapter_dirname)
			self._write_gitbook_file(os.path.join(chapter_dirname, 'README.md'), chapter['readme'])

			sections = chapter['sections']
			for jdx, section in enumerate(sections):
				section_filename = 'section-{}.md'.format(jdx)
				self._write_gitbook_file(os.path.join(chapter_dirname, section_filename), section['content'])


	def _write_gitbook_file(self, filename, content):
		with open(filename, 'w') as fwrite:
			fwrite.write('\n'.join(content))


	def _save_image(self, image, dirname):
		self._mkdir_anyway(dirname)

		result = None
		if not image.stream:
			raise Exception('No stream found')
		stream = image.stream.get_rawdata()
		filename = os.path.join(dirname, image.name)
		with open(filename, 'wb') as fwrite:
			fwrite.write(stream)
			fwrite.close()

