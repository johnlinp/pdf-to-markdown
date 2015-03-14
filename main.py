import sys
import pdf2md

def main(argv):
	if len(argv) == 2:
		page_num = int(argv[1])
		print 'Parsing page', page_num
	else:
		page_num = None
		print 'Parsing all pages'

	parser = pdf2md.Parser('neihu.pdf')
	parser.extract(page_num)
	piles = parser.parse(page_num)

	syntax = pdf2md.UrbanSyntax()

	writer = pdf2md.Writer()
	writer.set_syntax(syntax)
	writer.set_mode('simple')
	writer.set_title('neihu')
	writer.write(piles)

if __name__ == '__main__':
	main(sys.argv)

