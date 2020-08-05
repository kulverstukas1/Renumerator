'''
    Author: Kulverstukas
    Website: http://9v.lt
    Date: 2020-08-05
    Description:
        This script is to extract a given range of pages from
        a given PDF file and number the pages.
'''

import io
import re
import os
import sys
import argparse
from argparse import ArgumentTypeError
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

def initArgs():
    def checkPageArg(value):
        # first check if format is valid
        if (re.match("\d+-\d+", value)):
            pageNums = [int(i) for i in value.split("-")]
            # end page must be more than start page
            if (pageNums[0] > pageNums[1]):
                raise ArgumentTypeError("End page must be >= start page")
            # start page must be more than 0
            if (pageNums[0] <= 0): pageNums[0] = 1
            return pageNums
        else:
            raise ArgumentTypeError("Page format is invalid")

    def checkPdfFile(value):
        if (type(value) != str): raise ArgumentTypeError("File format is invalid")
        if (not os.path.isfile(value)): raise ArgumentTypeError("File does not exist")
        return PdfFileReader(open(value, "rb"))
    
    def validatePages(pdfReader, pages):
        if (pages[0] > pdfReader.getNumPages()): raise ArgumentTypeError("Start page is greater than the document size (%s)" % pdfReader.getNumPages())
        if (pages[1] > pdfReader.getNumPages()): pages[1] = pdfReader.getNumPages()
        return pages
        
    parser = argparse.ArgumentParser(description="Document splitter and renumerator")
    parser.add_argument('filename', metavar='filename.pdf', type=checkPdfFile, help='PDF name to process')
    parser.add_argument('pages', metavar='start-end', type=checkPageArg, help='Page range to extract')
    args = parser.parse_args()
    try:
        args.pages = validatePages(args.filename, args.pages)
    except ArgumentTypeError as err:
        parser.print_usage()
        print("%s: error: %s" % (sys.argv[0], err))
        exit()
    return args

def extractPages(pdf, start, end):
    newPdf = PdfFileWriter()
    for pageNum in range(start-1, end):
        newPdf.addPage(pdf.getPage(pageNum))
    return newPdf

def writeOut(pdf, filename):
    if (not os.path.isdir("out")):
        os.mkdir("out")
    outputStream = open("out/"+filename, "wb")
    pdf.write(outputStream)
    outputStream.close()
    
def addPageNums(pdf):
    newPdf = PdfFileWriter()
    for pageNum in range(pdf.getNumPages()):
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        can.rotate(270)
        can.drawString(-18*mm, 20*mm, str(pageNum+1))
        can.save()
        packet.seek(0)
        pageNumPdf = PdfFileReader(packet)
        page = pdf.getPage(pageNum)
        page.mergePage(pageNumPdf.getPage(0))
        newPdf.addPage(page)
    return newPdf

args = initArgs()
slicedPdf = extractPages(args.filename, args.pages[0], args.pages[1])
outPdf = addPageNums(slicedPdf)
writeOut(outPdf, "out_%d-%d.pdf" % (args.pages[0], args.pages[1]))
print("Done!")