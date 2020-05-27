import os
import sys
from glob import glob
import os
from os.path import basename
GS_OPTIONS="-dNOPAUSE -dBATCH -q -sPAPERSIZE=a4 -sDEVICE=png16m -dTextAlphaBits=4 -r720x720"

def main():
    inputdir    = sys.argv[1]
    outputdir   = sys.argv[2]
    for input_filename in glob(inputdir + '/*.pdf'):
        print(input_filename)
        filename = basename(input_filename)
        output_filename = '{outputdir}{sep}{filename}'.format(outputdir=outputdir                 
                                                            , sep=os.sep
                                                            , filename=filename.replace('.pdf','.png')) 
        gs_cmd = "gswin64c {options} -o {output_filename} {input_filename}".format(options=GS_OPTIONS
                                                                            ,output_filename=output_filename
                                                                            , input_filename=input_filename)
        os.system(gs_cmd)
        print('Created: {}'.format(output_filename))

if __name__ == '__main__':
    main()