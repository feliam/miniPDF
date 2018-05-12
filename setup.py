from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

import minipdf

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='minipdf',
    version=minipdf.__version__,
    url='https://github.com/feliam/miniPDF',
    license='Apache Software License',
    author='Felipe Andres Manzano',
    tests_require=['pytest'],
    install_requires=[],
    cmdclass={'test': PyTest},
    author_email='feliam@binamuse.com',
    description='A python library for making PDF files in a very low level way.',
    long_description=long_description,
    packages=['minipdf'],
    include_package_data=True,
    platforms='any',
    test_suite='minipdf.test.test_minipdf',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    scripts=['scripts/mkpdftext', 'scripts/mkpdfxfa', 'scripts/mkpdfotf', 'scripts/mkpdfjs'],
    #extras_require={
    #    'testing': ['pytest'],
    #}
)
