miniPDF
=======

A python library for making PDF files in a very low level way.

The legendary minipdf python library reaches github. This is a cleaner version of the old micro lib used in more than 10 PDF related exploits.

## Features
It supports only the most basic file structure (PDF3200:7.5.1), that’s it without incremental updates or linearization.

![](https://feliam.files.wordpress.com/2010/01/pdffilestructure.jpg?w=240)
* A one-line header identifying the version of the PDF specification to which the file conforms
* A body containing the objects that make up the document contained in the file
* A cross-reference table containing information about the indirect objects in the file
* A trailer giving the location of the cross-reference table and of certain special objects within the body of the file
    
Also all basic PDF types: null, references, strings, numbers, arrays and dictionaries.

## Example: A minimal text displaying PDF 
As an example Let's create a minimal text displaying PDF file in python using minipdf. The following graph outlines the simples possible structure:
![](http://feliam.files.wordpress.com/2010/01/minimalpdfstructure.jpg?w=600)

### The python script
First we import the lib and create a PDFDoc object representing a document in memory …
```python
from minipdf import *
doc = PDFDoc()
```

As shown in the last figure the main object is the *Catalog*. The next 3 lines construct a *Catalog* dictionary object, add it to the document and set it as the root object…

```python
catalog = PDFDict()
catalog['Type'] = PDFName('Catalog')
doc += catalog
doc.setRoot(catalog)
```

At this point we don’t even have a valid pdf but if we output the inclomplete PDF this is how the output will look like:

```
%PDF-1.5
%���
1 0 obj
<</Type /Catalog >>
endobj
xref
0 2
0000000000 65535 f 
0000000015 00000 n 
trailer
<</Root 1 0 R /Size 2 >>
startxref
50
%%EOF
```

As you can see, it's only a matter of adding all the different pdf objects link togheter from the *Catalog*. The library allows to add them in almost any order. Let’s try to follow the basic tree structure. To add a *page*, first we need a *pages* dictionary.
```
pages = PDFDict()
pages['Type'] = PDFName('Pages')
doc += pages
```

Which should be linked from the *Catalog*.

```
catalog['Pages'] = PDFRef(pages)
```

Then a *page*.

```
#page
page = PDFDict()
page['Type'] = PDFName('Page')
page['MediaBox'] = PDFArray([0, 0, 612, 792])
doc += page

#add parent reference in page
page['Parent'] = PDFRef(pages)
```

Which should be linked from the *pages* dictionary.

```
pages['Kids'] = PDFArray([PDFRef(page)])
pages['Count'] = PDFNum(1)
```

Now we add some content to the page. This is called a *content stream*.

```
contents = PDFStream('''BT 
/F1 24 Tf 0 700 Td 
%s Tj 
ET
'''%PDFString(sys.argv[1]))
doc += contents
```

The *content stream* is linked from the page

```
page['Contents'] = PDFRef(contents)
```

Note that in the *content stream* we are referencing a font name */F1*. We should define this font.

```
font = PDFDict()
font['Name'] = PDFName('F1')
font['Subtype'] = PDFName('Type1')
font['BaseFont'] = PDFName('Helvetica')
```

Associate each defined font with a name in a font map.

```
fontname = PDFDict()
fontname['F1'] = font
```

And add/link all that from the */Font* field of the *resource* dictionary.

```
#resources
resources = PDFDict()
resources['Font'] = fontname
doc += resources
```

Then linked the resources to it's page under the *Resources* field.

```
page['Resources'] = PDFRef(resources)
```

We are done! Just print the resulted document..

```
print doc
```

