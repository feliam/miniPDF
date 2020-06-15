import unittest
from minipdf import PDFDoc, PDFName, PDFNum, PDFString, PDFRef, PDFStream, PDFDict, PDFArray


class ManticoreTest(unittest.TestCase):
    _multiprocess_can_split_ = True

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_name(self):
        self.assertEqual(str(PDFName("NAME")), '/NAME')
        self.assertEqual(str(PDFName("/NAME")), '/#2fNAME')

