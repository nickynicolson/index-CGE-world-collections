import pandas as pd
from glob import glob
import sys
from os.path import basename
import re

def isVolField(s):
    volfield_flag = False
    if s is not None:
        volfield_flag = re.match('^[I1l]+$',s)
    return volfield_flag

def containsVolField(s):
    contains_flag = False
    if s is not None:
        contains_flag = (len([elem for elem in s.split(' ') if isVolField(elem)]) > 0)
    return contains_flag

def extractName(s):
    name = None
    if s is not None:
        elems = re.split('\s+', s)
        name_elems = []
        for elem in elems:
            if isVolField(elem):
                break
            name_elems.append(elem)
        name = ' '.join(name_elems)
    return name

def isNameField(s):
    namefield_flag = False
    if s is not None:
        namefield_flag = re.match('^[A-Z].*[a-z]$',s)
    return namefield_flag

def cleanName(s):
    cleaned = None
    if s is not None:
        elems = re.split('\s+', s)
        stripped_elem_count = 0
        name_elems = []
        for elem in elems:
            if not isNameField(elem):
                stripped_elem_count += 1
            else:
                break
        name_elems = elems[stripped_elem_count:]
        cleaned = ' '.join(name_elems)
    return cleaned

def main():
    inputdir    = sys.argv[1]
    outputfile  = sys.argv[2]
    dfs = []
    for i, input_filename in enumerate(glob(inputdir + '/*.txt')): 
        print(input_filename)
        df = pd.read_csv(input_filename, encoding='utf8',header=None,lineterminator='\n',delimiter='@~@#@')
        df['filename'] = [basename(input_filename)]*len(df)
        df['line_number']=list(range(0,len(df)))
        df['page_number']=[i]*len(df)
        dfs.append(df)
    df=pd.concat(dfs)
    df.rename(columns={0:'line'},inplace=True)
    df['contains_vol']=df.line.apply(containsVolField)
    mask = (df.contains_vol == True)
    df['name']=[None]*len(df)
    df.loc[mask,'name']=df[mask].line.apply(extractName)
    df['clean_name']=[None]*len(df)
    df.loc[mask,'clean_name']=df[mask].name.apply(cleanName)

    df.to_csv(outputfile,sep='\t',encoding='utf8',index=False)

if __name__ == '__main__':
    main() 