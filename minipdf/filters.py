import zlib,struct
from StringIO import StringIO
import logging
logger = logging.getLogger("FILTER")

#Some code in this file was inspired on ghoststcript C code.
#TODO: document and test A LOT, add at least 1 test per filter/perams convination
#Needs refactoring. The parameters part of the filters is not as clean as it could be.

#7.4   Filters
#Stream filters are introduced in 7.3.8, "Stream Objects." An option when reading 
#stream data is to decode it using a filter to produce the original non-encoded 
#data. Whether to do so and which decoding filter or filters to use may be specified 
#in the stream dictionary.

class PDFFilter(object):
    def __init__(self,params=None):
        self.setParams(params)
        self.default=None
        
    def getDefaultParams(self):
        return self.default
        
    def getParams(self):
        return (self.params == {} or self.params == None) and self.getDefaultParams() or self.params
        
    def setParams(self,params=None):
        self.params = {}
        self.params.update(self.getDefaultParams())
        self.params.update(params)
        #self.params =  not params and self.getDefaultParams() or params
        
    def decode(data):
        pass
        
    def encode(data):
        pass

#################################ASCIIHexDecode#########################################
class ASCIIHexDecode(PDFFilter):
    '''Decodes data encoded in an ASCII hexadecimal
       representation, reproducing the original binary data.
       
       The ASCIIHexDecode filter shall produce one byte of binary data for each 
       pair of ASCII hexadecimal digits (0-9 and A-F or a-f). All white-space 
       characters shall be ignored. A GREATER-THAN SIGN (3Eh) indicates EOD. 
       Any other characters shall cause an error. If the filter encounters the EOD 
       marker after reading an odd number of hexadecimal digits, it shall behave as
       if a 0 (zero) followed the last digit.
    '''
    default = {}
    name = 'ASCIIHexDecode'
    def __init__(self,params={}):
        PDFFilter.__init__(self,params)

    def decode(self, data):
        result = ""
        for c in data:
            if c in "0123456789ABCDEFabcdef":
                result+=c
            elif c == '>':
                break
            elif c not in "\x20\r\n\t\x0c\x00":
                continue
            else:
                raise "ERROR"
        result = result + '0'*(len(result)%2)
        return result.decode('hex')

    def encode(self, data):
        return data.encode('hex')

#################################ASCII85Decode#########################################
class ASCII85Decode(PDFFilter):
    '''
    7.4.3     ASCII85Decode Filter
    The ASCII85Decode filter decodes data that has been encoded in ASCII base-85 
    encoding and produces binary data. The following paragraphs describe the process 
    for encoding binary data in ASCII base-85; the ASCII85Decode filter reverses this 
    process. The ASCII base-85 encoding shall use the ASCII characters ! through u and
    the character z, with the 2-character sequence ~> as its EOD marker. The ASCII85Decode
    filter shall ignore all white-space characters. Any other characters, and any character
    sequences that represent impossible combinations in the ASCII base-85 encoding shall 
    cause an error.
    '''
    name='ASCII85Decode'
    def __init__(self,params={}):
        self.pad=False
        #This does not work. Most streams encoded with this use all chars. TODO:recheck
        #self._b85chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~"
        self._b85chars = [chr(x) for x in range(0,0xff)]
        self._b85chars2 = [(a + b) for a in self._b85chars for b in self._b85chars]
        self._b85dec = {}
        self.default = {}
        for i, c in enumerate(self._b85chars):
            self._b85dec[c] = i
        PDFFilter.__init__(self,params)

    def decode(self, text):
        """decode base85-encoded text"""
        #Remove whitespaces...
        text = ''.join([ c for c in text if not c in "\x20\r\n\t\x0c\x00" ])

        #Cut the stream at the eod
        eod = text.find('~>')
        if eod != -1:
            test=text[:eod]
    
        l = len(text)
        out = []
        for i in range(0, len(text), 5):
            chunk = text[i:i+5]
            acc = 0
            for j, c in enumerate(chunk):
                acc = acc * 85 + self._b85dec[c]
                
            #This does not work. Most streams encoded with this use all chars and overflow. TODO:recheck
            #    try:
            #        acc = acc * 85 + self._b85dec[c]
            #    except KeyError:
            #        raise TypeError('Bad base85 character at byte %d' % (i + j))
            #if acc > 4294967295:
            #    raise OverflowError('Base85 overflow in hunk starting at byte %d' % i)
            out.append(acc&0xffffffff)

        # Pad final chunk if necessary
        cl = l % 5
        if cl:
            acc *= 85 ** (5 - cl)
            if cl > 1:
                acc += 0xffffff >> (cl - 2) * 8
            out[-1] = acc

        out = struct.pack('>%dL' % (len(out)), *out)
        if cl:
            out = out[:-(5 - cl)]

        return out

    def encode(self, text):
        """encode text in base85 format"""
        l = len(text)
        r = l % 4
        if r:
            text += '\0' * (4 - r)
        longs = len(text) >> 2
        words = struct.unpack('>%dL' % (longs), text)

        out = ''.join(self._b85chars[(word // 52200625) % 85] +
                      self._b85chars2[(word // 7225) % 7225] +
                      self._b85chars2[word % 7225]
                      for word in words)

        if self.pad:
            return out

        # Trim padding
        olen = l % 4
        if olen:
            olen += 1
        olen += l // 4 * 5
        return out[:olen]



class Predictor():
    '''
    7.4.4.4   LZW and Flate Predictor Functions
    LZW and Flate encoding compress more compactly if their input data is highly 
    predictable. One way of increasing the predictability of many continuous-tone 
    sampled images is to replace each sample with the difference between that sample
    and a predictor function applied to earlier neighboring samples. If the predictor 
    function works well, the postprediction data clusters toward 0.

    1  No prediction (the default value)
    2  TIFF Predictor 2
    10 PNG prediction (on encoding, PNG None on all rows)
    11 PNG prediction (on encoding, PNG Sub on all rows)
    12 PNG prediction (on encoding, PNG Up on all rows)
    13 PNG prediction (on encoding, PNG Average on all rows)
    14 PNG prediction (on encoding, PNG Paeth on all rows)
    15 PNG prediction (on encoding, PNG optimum)

    '''
    def __init__(self,n=1,columns=1,bits=8):
        assert n in [1,2,10,11,12,13,14,15]
        self.predictor = n
        self.columns=columns
        self.bits=bits

    def encode(self):
        raise "Unsupported Predictor encoder"

    def decode(self, data):
        def decode_row(rowdata,prev_rowdata):
            if self.predictor == 1:
                return rowdata
            if self.predictor == 2:
                #TIFF_PREDICTOR
                bpp = (self.bits + 7) / 8
                for i in range(bpp+1, rowlength):
                    rowdata[i] = (rowdata[i] + rowdata[i-bpp]) % 256
            # PNG prediction
            elif self.predictor >= 10 and self.predictor <= 15:
                filterByte = rowdata[0]
                if filterByte == 0:
                    pass
                elif filterByte == 1:
                    # prior 
                    bpp = (self.bits + 7) / 8
                    for i in range(bpp+1, rowlength):
                        rowdata[i] = (rowdata[i] + rowdata[i-1]) % 256
                elif filterByte == 2:
                    # up
                    for i in range(1, rowlength):
                        rowdata[i] = (rowdata[i] + prev_rowdata[i]) % 256
                elif filterByte == 3:
                    # average 
                    bpp = (self.bits + 7) / 8
                    for i in xrange(1,bpp):
                        rowdata[i] = (rowdata[i] + prev_rowdata[i]/2) % 256
                    for j in xrange(i,rowlength):
                        rowdata[j] = (rowdata[j] + (rowdata[j-bpp] + prev_rowdata[j])/2) % 256
                elif filterByte == 4:
                    # paeth filtering 
                    bpp = (self.bits + 7) / 8;
                    for i in xrange(1,bpp):
                        rowdata[i] = rowdata[i] + prev_rowdata[i];
                    for j in xrange(i,rowlength):
                        # fetch pixels 
                        a = rowdata[j-bpp]
                        b = prev_rowdata[j]
                        c = prev_rowdata[j-bpp]

                        # distances to surrounding pixels 
                        pa = abs(b - c)
                        pb = abs(a - c)
                        pc = abs(a + b - 2*c)

                        # pick predictor with the shortest distance 
                        if pa <= pb and pa <= pc :  
                            pred = a
                        elif pb <= pc:
                            pred = b
                        else:
                            pred = c
                        rowdata[j] = rowdata[j] + pred

                else:
                    raise "Unsupported PNG filter %r" % filterByte
                return rowdata
#begin
        rowlength = self.columns + 1
        assert len(data) % rowlength == 0
        if self.predictor == 1 :
            return data
        output = StringIO()
        # PNG prediction can vary from row to row
        prev_rowdata = (0,) * rowlength
        for row in xrange(0,len(data) / rowlength):
#            print (row*rowlength),((row+1)*rowlength),len(data) / rowlength
            rowdata = decode_row([ord(x) for x in data[(row*rowlength):((row+1)*rowlength)]],prev_rowdata)
            if self.predictor in [1,2]:
                output.write(''.join([chr(x) for x in rowdata[0:]]))
            else:
                output.write(''.join([chr(x) for x in rowdata[1:]]))
            prev_rowdata = rowdata
        data = output.getvalue()
        return data


class FlateDecode(PDFFilter):
    '''
    The Flate method is based on the public-domain zlib/deflate compression method, 
    which is a variable-length Lempel-Ziv adaptive compression method cascaded with 
    adaptive Huffman coding. It is fully defined in Internet RFCs 1950, ZLIB Compressed 
    Data Format Specification, and 1951, DEFLATE Compressed Data Format Specification
    '''
    default = { 'Predictor': 1, 
                'Columns' : 0,
                'Colors' : 1,
                'BitsPerComponent': 8}
    name = "Fl"
    #name = "FlateDecode"
    def __init__(self,params={}):
        PDFFilter.__init__(self,params)

    def decode(self, data):
        p = self.getParams()
        data = data.decode('zlib')
        data = Predictor(int(p['Predictor']),int(p['Columns']),int(p['BitsPerComponent'])).decode(data)
        return data

    def encode(self, data):
        assert self.getParams()['Predictor'] == 1
        return data.encode('zlib')

import lzw
class LZWDecode(PDFFilter):
    '''
    7.4.4.2   Details of LZW Encoding
    LZW (Lempel-Ziv-Welch) is a variable-length, adaptive compression method
    that has been adopted as one of the standard compression methods in the 
    Tag Image File Format (TIFF) standard. 

    Data encoded using the LZW compression method shall consist of a sequence 
    of codes that are 9 to 12 bits long. Each code shall represent a single 
    character of input data (0-255), a clear-table marker (256), an EOD marker
    (257), or a table entry representing a multiple-character sequence that has
    been encountered previously in the input (258 or greater).
    '''
    default = { 'Predictor': 1, 
                'Columns' : 1,
                'Colors' : 1,
                'BitsPerComponent': 8,
                'EarlyChange': 1 }
    name = "LZW" #Decode
    def __init__(self,params=None):
        PDFFilter.__init__(self, self.default)

    def decode(self, data):
        assert self.getParams()['EarlyChange']==1
        data = lzw.decompress(data)
        data = Predictor(p['Predictor'],p['Columns'],p['BitsPerComponent']).decode(data)
        return data

    def encode(self, data):
        assert self.getParams()['EarlyChange']==1
        assert self.getParams()['Predictor']==1
        return ''.join(lzw.compress(data))

class RunLengthDecode(PDFFilter):
    '''Decompresses data encoded using a byte-oriented run-length encoding algorithm,
       reproducing the original text or binary data (typically monochrome image data,
       or any data that contains frequent long runs of a single byte value).

       The RunLengthDecode filter decodes data that has been encoded in a simple byte-oriented
       format based on run length. The encoded data shall be a sequence of runs, where each run
       shall consist of a length byte followed by 1 to 128 bytes of data. If the length byte is
       in the range 0 to 127, the following length + 1 (1 to 128) bytes shall be copied literally
       during decompression. If length is in the range 129 to 255, the following single byte shall
       be copied 257 - length (2 to 128) times during decompression. A length value of 128 shall 
       denote EOD.
    '''
    name = "RunLengthDecode"
    default = {}
    def __init__(self,params={}):
        PDFFilter.__init__(self,params)

    def decode(self, data):
        inp = StringIO(data)
        out = StringIO()
        try:
            while True:
                n = ord(inp.read(1))
                if n < 127:
                    out.write(inp.read(n+1))
                else:
                    out.write(inp.read(1)*(257-n))
        except:
            pass
        return out.getvalue()

    def encode(self, data):
        #Trivial encoding x2 in size
        out = StringIO()
        for c in data:
            out.write("\x00"+c)
        return out.getvalue()




### filter multiplexers....
def defilterData(filtername,stream,params=None):
    logger.debug("Filtering stream with %s"%repr((filtername,params)))
    if filtername == "FlateDecode":
        return FlateDecode(params).decode(stream)
    elif filtername == "LZWDecode":
        return LZWDecode(params).decode(stream)
    elif filtername == "ASCIIHexDecode":
        return ASCIIHexDecode(params).decode(stream)
    elif filtername == "ASCII85Decode":
        return ASCII85Decode(params).decode(stream)
    elif filtername == "RunLengthDecode":
        return RunLengthDecode(params).decode(stream)

def filterData(filtername,stream,params=None):
    if filtername == "FlateDecode":
        return FlateDecode(params).encode(stream)
    elif filtername == "ASCIIHexDecode":
        return ASCIIHexDecode(params).encode(stream)
    
if __name__ == "__main__":
    pass

