''' This generates a minimal pdf that renders a jpeg file '''
import os
import zlib
import sys
from minipdf import *

def make(data):
    doc = PDFDoc()

    #pages
    pages = PDFDict()
    pages['Type'] = PDFName('Pages')

    #catalog
    catalog = PDFDict()
    catalog['Type'] = PDFName('Catalog')
    catalog['Pages'] = PDFRef(pages)

    #lets add those to doc just for showing up the Ref object.
    doc+=catalog
    doc+=pages
    #Set the pdf rootpoython
    doc.setRoot(catalog)

    try:
        from PIL import Image
        from StringIO import StringIO
        im = Image.open( StringIO(data))
        _width, _height = im.size
        filter_name = {'JPEG2000':'JPXDecode',
                  'JPEG': 'DCTDecode'} [im.format]
    except Exception, e:
        _width=256
        _height=256

##XOBJECT
    xobj = PDFStream(data)
    xobj['Type'] = PDFName('XObject')
    xobj['Subtype'] = PDFName('Image')
    xobj['Width'] = PDFNum(_width)
    xobj['Height'] = PDFNum(_height)
    xobj['ColorSpace'] = PDFName('DeviceRGB')
    xobj['BitsPerComponent'] = PDFNum(8)
    xobj['Filter'] = PDFName(filter_name)
    
    contents = PDFStream('q %d 0 0 %d 0 0 cm /Im1 Do Q' % (_width, _height))
    resources = PDFDict()
    resources['ProcSet'] = PDFArray([PDFName('PDF'), PDFName('ImageC'), PDFName('ImageI'), PDFName('ImageB')])
    
    Im1=PDFDict()
    Im1['Im1'] = PDFRef(xobj)
    resources['XObject'] = Im1
    
    #The pdf page
    page = PDFDict()
    page['Type'] = PDFName('Page')
    page['Parent'] = PDFRef(pages)
    page['MediaBox'] = PDFArray([ 0, 0, _width, _height])
    page['Contents'] = PDFRef(contents)
    page['Resources'] = PDFRef(resources)

    [doc.append(x) for x in [xobj, contents, resources, page]]
    pages['Count'] = PDFNum(1)
    pages['Kids'] = PDFArray([PDFRef(page)])
    return doc



##Main
if __name__=='__main__':
    print make(file(sys.argv[1], 'rb').read())

