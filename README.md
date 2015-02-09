# PDF To Markdown

This is NOT a general-purpose converter.
Currently only for urban planning document in Taiwan.

## System Requirement

You should install pdfminer first.

	git clone git@github.com:euske/pdfminer.git
	cd pdfminer
	make cmap
	sudo python setup.py install

The `make cmap` is necessary for documents containing Chinese characters.

