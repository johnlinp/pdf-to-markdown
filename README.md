# PDF To Markdown

This is NOT a general-purpose converter.
Currently only for urban planning document in Taiwan.


## Demo

From [this PDF file](https://github.com/johnlinp/pdf-to-markdown/blob/master/examples/neihu.pdf?raw=true), we generate:

- [Gitbook version](http://johnlinp.gitbooks.io/neihu/content/)
- [Simple markdown](https://github.com/johnlinp/pdf-to-markdown/tree/master/examples/neihu.md)


## System Requirement

You should install `pdfminer.six` first.

	sudo pip install pdfminer.six


# Usage

After you downloaded `pdf-to-markdown`

	git clone https://github.com/johnlinp/pdf-to-markdown.git
	cd pdf-to-markdown

Just type

	python2 main.py <pdf>

For example, you can use our example PDF file:

	python2 main.py examples/neihu.pdf

