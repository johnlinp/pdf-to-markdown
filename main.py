import sys
import os
import pdf2md

def main(argv):
	if len(argv) == 2:
		filename = argv[1]
		title = os.path.splitext(os.path.basename(filename))[0]
		print 'Parsing', filename
	else:
		print 'usage:'
		print '    python main.py <pdf>'
		return

	parser = pdf2md.Parser(filename)
	parser.extract()
	piles = parser.parse()

	syntax = pdf2md.UrbanSyntax()

	writer = pdf2md.Writer()
	writer.set_syntax(syntax)
	writer.set_mode('simple')
	writer.set_title(title)
	writer.write(piles)

	print 'Your markdown is at', writer.get_location()

if __name__ == '__main__':
	main(sys.argv)

