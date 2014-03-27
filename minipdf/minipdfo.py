## UNFINISHED -UNFINISHED -UNFINISHED -UNFINISHED -UNFINISHED -UNFINISHED -UNFINISHED -UNFINISHED -
## This is a preliminary version, lots of tricks are still to be implemented... 
## Anyway if you find some trick not coded here, let me know! 
## Let me implement some of the ways...
## http://feliam.wordpress.com 

## Ref: Some of this first pointed out in ...  
##      http://blog.didierstevens.com/2008/04/29/pdf-let-me-count-the-ways/


import random

decoys=[
'''<</Type /Catalog /Pages 2 0 R >>'''
'''<</Count 1 /Kids [3 0 R] /Type /Pages >>'''
'''<</Parent 2 0 R /MediaBox [0 0 595 894] /ProcSet [/PDF /Text] /Resources <</Font <</F1 <</BaseFont /Times-Roman /Subtype /Type1 /Name /F1 /Encoding /WinAnsiEncoding >> >> >> /Type /Page /Contents 4 0 R >>'''
'''4 0 obj'''
'''endstream'''
'''endobj'''
'''xref'''
'''0000000339 00000 n '''
'''trailer'''
'''<</Root 1 0 R /Size 5 >>'''
'''startxref'''
]
delimiters = list('()<>[]{}/%')
whitespaces = list('\x20\x0a\x0c\x0d')
EOL = '\x0A'

def putSome(l):
    some = ""
    size = random.randint(0,5)
    for i in range(0,size):
        some += random.choice(l)
    return some 

def getSeparator():
    if random.randint(0,100)<40:
        return random.choice(["\00","\x09","\0a","\x0d","\x20"])
    elif random.randint(0,100)<101:
        return "%"+random.choice(decoys)+EOL

import struct

#For constructing a minimal pdf file
class PDFObject:
    def __init__(self):
        self.n=None
        self.v=None

    def __str__(self):
        raise "Fail"

class PDFDict(PDFObject):
    def __init__(self, d={}):
        PDFObject.__init__(self)
        self.dict = {}
        for k in d:
            self.dict[k]=d[k]

    def add(self,name,obj):
        self.dict[name] = obj

    def __str__(self):
        s="<<"
        s+=random.choice(["\00","\x09","\0a","\x0c","\x0d","\x20"])
        for name in self.dict:
            s+="%s%c"%(PDFName(name).__str__(),
            s+=getSeparator()
            s+="%s"%self.dict[name]
            s+=getSeparator()
        s+=">>"
        s+=getSeparator()
        return s

class PDFStream(PDFDict):
    def __init__(self,stream=""):
        PDFDict.__init__(self)
        self.stream=stream
        self.filtered=self.stream
        self.filters = []

    def appendFilter(self, filter):
        self.filters.append(filter)
        self._applyFilters() #yeah every time .. so what!

    def _applyFilters(self):
        self.filtered = self.stream
        for f in self.filters:
                self.filtered = f.encode(self.filtered)
        self.add('Length', len(self.filtered))
        if len(self.filters)>0:
            self.add('Filter', PDFArray([f.name for f in self.filters]))
        #Add Filter parameters ?

    def __str__(self):
        self._applyFilters() #yeah every time .. so what!
        s=""
        s+=PDFDict.__str__(self)
        s+="\nstream\n"
        s+=self.filtered
        s+="\nendstream"
        return s

class PDFArray(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        self.s=s
    def __str__(self):
        return "[%s]"%(random.choice(whitespaces).join([ o.__str__() for o in self.s]))


##7.3.5 Name Objects
class PDFName(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        self.s=s
    def __str__(self):
        obfuscated = ""
        for c in self.s:
            r=random.randint(0,100)
            if (ord(c)<=ord('!') and ord(c) >= ord('~')) or r < 50:
                obfuscated+='#%02x'%ord(c)
            else:
                obfuscated+=c
        return "/%s"%obfuscated

##7.3.4.3 Hexadecimal Strings
class PDFHexString(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        self.s=s

    def __str__(self):
        return "<" + "".join(["%02x"%ord(c) for c in self.s]) + ">"

class PDFOctalString(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        self.s="".join(["\\%03o"%ord(c) for c in s])

    def __str__(self):
        return "(%s)"%self.s


##7.3.4.2 Literal Strings
class PDFString(PDFObject):
    escapes = {'\x0a': '\\n',
    '\x0d': '\\r', 
    '\x09': '\\t',
    '\x08': '\\b',
    '\xff': '\\f',
    '(':    '\\(',
    ')':    '\\)',
    '\\':    '\\\\', }

    def __init__(self,s):
        PDFObject.__init__(self)
        self.s=s

    def __str__(self):
        if random.randint(0,100) < 10:
            return PDFHexString(self.s).__str__()
        obfuscated = ""
        for c in self.s:
            if random.randint(0,100)>70:
                 obfuscated+='\\%03o'%ord(c)
            elif c in self.escapes.keys():
                 obfuscated+=self.escapes[c]
            else:
                obfuscated+=c
            if random.randint(0,100) <10 :
                obfuscated+='\\\n'
        return "(%s)"%obfuscated


class PDFNum(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        self.s=s

    def __str__(self):
        sign = ""
        if random.randint(0,100)>50:
            if self.s>0:
                sign = '+'
            elif self.s<0:
                sign = '-'
            elif random.randint(0,100)>50:
                sign = '-'
            else:
                sign = '+'
        obfuscated = ""
        obfuscated += sign
        obfuscated += putSome(['0'])
        obfuscated += "%s"%self.s
        if type(self.s)==type(0):
            if random.randint(0,100)>60:
                obfuscated += "."+putSome(['0'])
        else:
            if random.randint(0,100)>60:
                obfuscated += putSome(['0'])
        return obfuscated

class PDFBool(PDFObject):
    def __init__(self,s):
        PDFObject.__init__(self)
        self.s=s

    def __str__(self):
        if self.s:
            return "true"
        return "false"

class PDFRef(PDFObject):
    def __init__(self,obj):
        PDFObject.__init__(self)
        self.obj=[obj]
    def __str__(self):
        return "%d %d R"%(self.obj[0].n,self.obj[0].v)

class PDFNull(PDFObject):
    def __init__(self):
        PDFObject.__init__(self)

    def __str__(self):
        return "null"


class PDFDoc():
    def __init__(self,obfuscate=0):
        self.objs=[]
        self.info=None
        self.root=None

    def setRoot(self,root):
        self.root=root

    def setInfo(self,info):
        self.info=info

    def _add(self,obj):
        obj.v=0
        obj.n=1+len(self.objs)
        self.objs.append(obj)

    def add(self,obj):
        if type(obj) != type([]):
            self._add(obj)
        else:
            for o in obj:  
                self._add(o)

    def _header(self):
##Adobe suplement to ISO3200 3.4.1 File Header
        header = "%"+random.choice(['!PS','PDF'])+"-%d.%d"%(random.randint(0,0xffffffff),random.randint(0,0xffffffff))
        crap = ""
        while len(crap) < random.randint(4,1024):
            crap=crap+chr(random.choice(list(set(range(0,256))- set([chr(i) for i in [0x0a,0x0d]]))))
        while len(header)<1024:
            header = chr(random.randint(0,255))+header

        return header+"\n%"+crap+"\n"

    def __str__(self):
        doc1 = self._header()
        xref = {}
        for obj in self.objs:
            xref[obj.n] = len(doc1)
            doc1+="%d %d obj\n"%(obj.n,obj.v)
            doc1+=obj.__str__()
            doc1+="\nendobj\n" 
        posxref=len(doc1)
        doc1+="xref\n"
        doc1+="0 %d\n"%(len(self.objs)+1)
        doc1+="0000000000 65535 f \n"
        for xr in xref.keys():
            doc1+= "%010d %05d n \n"%(xref[xr],0)
        doc1+="trailer\n"
        trailer =  PDFDict()
        trailer.add("Size",len(self.objs)+1)
        trailer.add("Root",PDFRef(self.root))
        if self.info:
            trailer.add("Info",PDFRef(self.info))
        doc1+=trailer.__str__()
        doc1+="\nstartxref\n%d\n"%posxref
        doc1+="%%EOF"

        return doc1

