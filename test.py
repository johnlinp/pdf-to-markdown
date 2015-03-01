import os
import sys
import glob
import filecmp
from converter import Converter

def main(argv):
	filename = 'neihu.pdf'
	converter = Converter(filename)
	converter.parse(5)

	print filename
	for page_num in range(122):
		test_page_path = os.path.join('tests', filename, str(page_num))
		if not os.path.exists(test_page_path):
			continue

		converter.convert(page_num)

		print '    Page', page_num
		for test_part in glob.glob(os.path.join(test_page_path, 'part*.md')):
			new_part = os.path.basename(test_part)
			print '        ', new_part,
			if filecmp.cmp(test_part, new_part):
				print 'Passed'
			else:
				print 'Failed'

		for new_part in glob.glob('part*'):
			os.remove(new_part)

if __name__ == '__main__':
	main(sys.argv)

