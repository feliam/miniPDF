##########################################################################
####   Felipe Andres Manzano     *   felipe.andres.manzano@gmail.com  ####
####   http://twitter.com/feliam *   http://wordpress.com/feliam      ####
##########################################################################
import struct

#For constructing a minimal pdf file
## PDF REference 3rd edition:: 3.2 Objects
class PDFObject(object):
    def __init__(self):
        self.n=None
        self.v=None
    def __str__(self):
        raise NotImplemented()

## PDF REference 3rd edition:: 3.2.1 Booleans Objects
class PDFBool(PDFObject):
    def __init__(self, val):
        assert type(val)==bool
        super(PDFBool, self).__init__()
        self.val = val
    def __str__(self):
        if self.val:
            return 'true'
        return 'false'

## PDF REference 3rd edition:: 3.2.2 Numeric Objects
class PDFNum(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        self.s=s
    def __str__(self):
        return '%s'%self.s

## PDF REference 3rd edition:: 3.2.3 String Objects
class PDFString(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        self.s=s
    def __str__(self):
        return '(%s)'%self.s.replace(')','\\%03o'%ord(')'))

## PDF REference 3rd edition:: 3.2.3 String Objects / Hexadecimal Strings
class PDFHexString(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        self.s=s
    def __str__(self):
        return '<' + ''.join(['%02x'%ord(c) for c in self.s]) + '>'

## A convenient type of literal Strings
class PDFOctalString(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        self.s=''.join(['\\%03o'%ord(c) for c in s])
    def __str__(self):
        return '(%s)'%self.s

## PDF REference 3rd edition:: 3.2.4 Name Objects
class PDFName(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        self.s=s
    def __str__(self):
        return '/%s'%self.s

## PDF REference 3rd edition:: 3.2.5 Array Objects
class PDFArray(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        assert type(s) == type([])
        self.s=s
    def append(self,o):
        self.s.append(o)
        return self
    def __len__(self):
        return len(self.s)
    def __str__(self):
        return '[%s]'%(' '.join([ o.__str__() for o in self.s]))

## PDF REference 3rd edition:: 3.2.6 Dictionary Objects
class PDFDict(PDFObject, dict):
    def __init__(self, d={}):
        super(PDFDict, self).__init__()
        for k in d:
            self[k]=d[k]

    def __str__(self):
        s='<<'
        for name in self:
            s+='%s %s '%(PDFName(name),self[name])
        s+='>>'
        return s

## PDF REference 3rd edition:: 3.2.7 Stream Objects
class PDFStream(PDFDict):
    def __init__(self,stream=''):
        super(PDFDict, self).__init__()
        self.stream=stream
        self.filtered=self.stream
        self['Length'] = len(stream)
        self.filters = []

    def appendFilter(self, filter):
        self.filters.append(filter)
        self._applyFilters() #yeah every time .. so what!

    def _applyFilters(self):
        self.filtered = self.stream
        for f in reversed(self.filters):
                self.filtered = f.encode(self.filtered)
        if len(self.filters)>0:
            self['Length'] = len(self.filtered)
            self['Filter'] = PDFArray([PDFName(f.name) for f in self.filters])
        #Add Filter parameters ?
    def __str__(self):
        self._applyFilters() #yeah every time .. so what!
        s=''
        s+=PDFDict.__str__(self)
        s+='\nstream\n'
        s+=self.filtered
        s+='\nendstream'
        return s

## PDF REference 3rd edition:: 3.2.8 Null Object
class PDFNull(PDFObject):
    def __init__(self):
        PDFObject.__init__(self)

    def __str__(self):
        return 'null'

## PDF REference 3rd edition:: 3.2.9 Indirect Objects
class PDFRef(PDFObject):
    def __init__(self,obj):
        PDFObject.__init__(self)
        self.obj=[obj]
    def __str__(self):
        if self.obj[0].n is None:
            raise Exception("Cannot take a reference of " + str(self.obj[0]) + "because it is not added to any PDF Document")

        return '%d %d R'%(self.obj[0].n,self.obj[0].v)

## PDF REference 3rd edition:: 3.4 File Structure
## Simplest file structure...
class PDFDoc(list):
    def __init__(self,obfuscate=0):
        self.info=None
        self.root=None
    def setRoot(self,root):
        self.root=root
    def setInfo(self,info):
        self.info=info

    def __iadd__(self, x):
        self.append(x)
        return self

    def append(self,obj):
        assert isinstance(obj, PDFObject)
        if obj.v!=None or obj.n!=None:
            raise Exception('Object '+ repr(obj) +' has been already added to a PDF Document!')
        obj.v=0
        obj.n=1+len(self)
        super(PDFDoc, self).append(obj)

    def __str__(self):
        doc1 = '%PDF-1.5\n%\xE7\xF3\xCF\xD3\n'
        xref = {}
        for obj in self:
            #doc1+=file('/dev/urandom','r').read(100000)
            xref[obj.n] = len(doc1)
            doc1+='%d %d obj\n'%(obj.n,obj.v)
            doc1+=str(obj)
            doc1+='\nendobj\n' 
        #doc1+=file('/dev/urandom','r').read(100000)
        posxref=len(doc1)
        doc1+='xref\n'
        doc1+='0 %d\n'%(len(self)+1)
        doc1+='0000000000 65535 f \n'
        for xr in xref.keys():
            doc1+= '%010d %05d n \n'%(xref[xr],0)
        doc1+='trailer\n'
        trailer =  PDFDict()
        trailer['Size'] = len(self)+1
        trailer['Root'] = PDFRef(self.root)
        if self.info:
            trailer['Info'] = PDFRef(self.info)
        doc1+=str(trailer)
        doc1+='\nstartxref\n%d\n'%posxref
        doc1+='%%EOF'
        return doc1
