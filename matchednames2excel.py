import pandas as pd
import sys

def conv_filename(s):
    return s.replace('.txt','.pdf')

def main():
    inputfile   = sys.argv[1]
    outputfile  = sys.argv[2]
    df = pd.read_csv(inputfile, sep='\t', encoding='utf8')
    df['ipni_link'] = [None] * len(df)
    mask = df.id.notnull()
    df.loc[mask,'ipni_link'] = df[mask].id.apply(lambda id: '=HYPERLINK("http://ipni.org/n/{id}", "{id}")'.format(id=id))
    df['pdf_filename']=df.filename.apply(conv_filename)
    df['pageimage_link'] = df.pdf_filename.apply(lambda filename: '=HYPERLINK("pdfpages/{filename}","{filename}")'.format(filename=filename))    
    # drop the unused columns (name "window", interediate filenames etc)
    df.drop(columns=['filename','pdf_filename','name_min','name_max'],inplace=True)
    df.to_excel(outputfile)

if __name__ == '__main__':
    main()