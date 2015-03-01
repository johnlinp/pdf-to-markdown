import sys
from converter import Converter

def main(argv):
	if len(argv) == 2:
		page_num = int(argv[1])
	else:
		page_num = 13

	converter = Converter('neihu.pdf')
	converter.parse(page_num)
	converter.convert(page_num)

if __name__ == '__main__':
	main(sys.argv)

