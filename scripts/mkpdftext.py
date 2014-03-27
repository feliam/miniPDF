#! /usr/bin/env python
'''
This creates a minimal PDF file displaying text.

Usage:

./mkpdftext.py  "Hello World!" > hello.pdf

Ref. https://github.com/feliam/miniPDF
'''

import sys
from minipdf import PDFDoc, PDFName, PDFNum, PDFString, PDFRef, PDFStream, PDFDict, PDFArray

#The document
doc = PDFDoc()

#font
font = PDFDict()
font['Name'] = PDFName('F1')
font['Subtype'] = PDFName('Type1')
font['BaseFont'] = PDFName('Helvetica')

#name:font map
fontname = PDFDict()
fontname['F1'] = font

#resources
resources = PDFDict()
resources['Font'] = fontname
doc += resources

#contents
contents = PDFStream('''BT 
/F1 24 Tf 0 700 Td 
%s Tj 
ET
'''%PDFString(sys.argv[1]))
doc += contents

#page
page = PDFDict()
page['Type'] = PDFName('Page')
page['MediaBox'] = PDFArray([0, 0, 612, 792])
page['Contents'] = PDFRef(contents)
page['Resources'] = PDFRef(resources)
doc += page

#pages
pages = PDFDict()
pages['Type'] = PDFName('Pages')
pages['Kids'] = PDFArray([PDFRef(page)])
pages['Count'] = PDFNum(1)
doc += pages

#add parent reference in page
page['Parent'] = PDFRef(pages)

#catalog
catalog = PDFDict()
catalog['Type'] = PDFName('Catalog')
catalog['Pages'] = PDFRef(pages)
doc += catalog

doc.setRoot(catalog)
print doc

#@feliam
