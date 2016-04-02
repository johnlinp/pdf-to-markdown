# PDF To Markdown

This is NOT a general-purpose converter.
Currently only for urban planning document in Taiwan.


## Demo

From [this PDF file](https://github.com/johnlinp/pdf-to-markdown/blob/master/examples/neihu.pdf?raw=true), we generate:

- [Gitbook version](http://johnlinp.gitbooks.io/neihu/content/)
- [Simple markdown](https://github.com/johnlinp/pdf-to-markdown/tree/master/examples/neihu.md)


## System Requirement

You should install pdfminer first.

### If your PDF file doesn't contain Chinese Characters

	sudo apt-get install python-pdfminer

### Else

	git clone git@github.com:euske/pdfminer.git
	cd pdfminer
	make cmap
	sudo python setup.py install

The `make cmap` is necessary for documents containing Chinese characters.


# Usage

Just type

	python main.py <pdf>

For example, you can use our example PDF file:

	python main.py examples/neihu.pdf

