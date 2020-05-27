import pandas as pd
import sys

def main():
    inputfile   = sys.argv[1]
    outputfile  = sys.argv[2]
    df = pd.read_csv(inputfile, sep='\t', encoding='utf8')
    df['ipni_link'] = [None] * len(df)
    mask = df.id.notnull()
    df.loc[mask,'ipni_link'] = df[mask].id.apply(lambda id: '=HYPERLINK("http://ipni.org/n/{id}", "{id}")'.format(id=id))
    df['pageimage_link'] = df.filename.apply(lambda filename: '=HYPERLINK("pageimages/{filename}","{filename}")'.format(filename=filename.replace('.txt','.png')))    
    # drop the columns showing the name "window"
    df.drop(columns=['name_min','name_max'],inplace=True)
    df.to_excel(outputfile)

if __name__ == '__main__':
    main()