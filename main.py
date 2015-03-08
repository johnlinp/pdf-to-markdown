import sys
from converter import Converter
from writer import Writer

def main(argv):
	if len(argv) == 2:
		page_num = int(argv[1])
		print 'Parsing page', page_num
	else:
		page_num = None
		print 'Parsing all pages'

	converter = Converter('neihu.pdf')
	converter.extract(page_num)
	markdown = converter.convert(page_num)

	writer = Writer()
	writer.set_mode('simple')
	writer.set_title('neihu')
	writer.write(markdown)

if __name__ == '__main__':
	main(sys.argv)

