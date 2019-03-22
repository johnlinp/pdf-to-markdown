import os
from setuptools import setup

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(name='pdf-to-markdown',
    version='0.1.0',
    description='Convert PDF files into markdown files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='johnlinp',
    author_email='johnlinp@gmail.com',
    url='https://github.com/johnlinp/pdf-to-markdown',
    license='New BSD License',
    install_requires=[
        'pdfminer.six',
    ],
    packages=[
        'pdf2md',
    ],
    scripts=[
        'bin/pdf2md',
    ],
)
