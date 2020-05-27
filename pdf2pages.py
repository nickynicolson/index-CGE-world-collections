import os
from PyPDF2 import PdfFileReader, PdfFileWriter
import sys
from glob import glob
import os
from os.path import basename

def main():
    inputdir    = sys.argv[1]
    outputdir   = sys.argv[2]
    for inputfile in glob(inputdir + '/*.pdf'):
        print(inputfile)
        filename = basename(inputfile)
        content = filename.split('_')[1].split(' ')[0]
        pdf = PdfFileReader(inputfile)
        for page in range(pdf.getNumPages()):
            pdf_writer = PdfFileWriter()
            pdf_writer.addPage(pdf.getPage(page))
            output_filename = '{outputdir}{sep}{content}-page-{page}.pdf'.format(outputdir=outputdir                 
                                                                            , sep=os.sep
                                                                            , content=content
                                                                            , page=str(page+1).zfill(2)) 
            with open(output_filename, 'wb') as out:
                pdf_writer.write(out)
            print('Created: {}'.format(output_filename))

if __name__ == '__main__':
    main()