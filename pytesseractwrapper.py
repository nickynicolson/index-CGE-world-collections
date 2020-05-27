import pytesseract
import sys
from glob import glob
import os
from os.path import basename

def image_ocr(image_path, output_txt_file_name):
  # Configuration details for psm given by the command: 
  # tesseract --help-psm
  image_text = pytesseract.image_to_string(image_path, lang='eng+ces', config='--psm 6')
  with open(output_txt_file_name, 'w+', encoding='utf-8') as f:
    f.write(image_text)

def main():
    inputdir    = sys.argv[1]
    outputdir   = sys.argv[2]
    for input_filename in glob(inputdir + '/*.png'):
        print(input_filename)
        filename = basename(input_filename)
        output_filename = '{outputdir}{sep}{filename}'.format(outputdir=outputdir                 
                                                            , sep=os.sep
                                                            , filename=filename.replace('.png','.txt')) 
        image_ocr(input_filename, output_filename)

if __name__ == '__main__':
    main()