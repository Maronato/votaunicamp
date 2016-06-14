#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
import os
import re


def convert_pdf(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    os.remove(path)
    parser = PDFParser(fp)
    try:
        doc = PDFDocument(parser)
    except:
        return 0
    parser.set_document(doc)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,        password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    text = retstr.getvalue()
    fp.close()
    device.close()
    retstr.close()
    return text


def get_field(field, string):
    try:
        text = re.findall(r''+re.escape(field)+'\\n(.*?)\\n', string)
        text = text[0]
    except:
        return 0
    return text
