import pandas as pd
import sys
from Levenshtein import distance
from unidecode import unidecode

def readNameData(filename):
    df = pd.read_csv(filename, sep='|', encoding='utf8')
    print('Read in {} names'.format(len(df)))
    mask =  (
            (df.top_copy_b=='t')
            & (df.rank_s_alphanum.isin(['fam.','gen.']))
            & ((df.publication_year_i.isnull())|(df.publication_year_i<1970))
            & df.publishing_author_s_lower.notnull() 
            )
    df.drop(df[~mask].index,inplace=True)
    print('Retained {} names'.format(len(df)))
    columns = ['id','top_copy_b','publication_year_i','taxon_scientific_name_s_lower','publishing_author_s_lower']
    drop_columns = [col for col in df.columns if col not in columns]
    df.drop(columns=drop_columns, inplace=True)
    df['ipni_name_auth']=df.apply(lambda row: '{} {}'.format(row['taxon_scientific_name_s_lower'],row['publishing_author_s_lower']),axis=1)
    df.sort_values(by='ipni_name_auth',inplace=True)
    return df

def main():
    inputfile   = sys.argv[1]
    namefile    = sys.argv[2]
    outputfile  = sys.argv[3]

    # Read OCR-d list data
    df = pd.read_csv(inputfile, sep='\t', encoding='utf8')
    # Add ID 
    df['line_id']=list(range(0,len(df)))
    # Remove any accents
    mask=df.clean_name.notnull()
    df.loc[mask,'clean_name']=df[mask].clean_name.apply(unidecode)
    # Read IPNI name data
    dfn = readNameData(namefile)

    # First step match is identical match on name and author 
    df=pd.merge(left=df,right=dfn[['id','ipni_name_auth']],left_on='clean_name',right_on='ipni_name_auth',how='left')
    print('Matched {} names'.format(len(df[df['id'].notnull()])))
    df['match_stage']=[None]*len(df)
    df.loc[df['id'].notnull(),'match_stage']=0
    #
    # As the name list is alphabetical, each identical match can be used 
    # to constrain the search space of names for the unmatched list entries
    #
    # Add two columns to hold the min and max names to form the search "window"
    df['name_min']=[None]*len(df)
    df['name_max']=[None]*len(df)
    # Copy across identical match results as the start of the window
    df['name_min']=df['ipni_name_auth']
    # Using only matched entries, copy the next matched name as the end of the window
    mask=(df['ipni_name_auth'].notnull())
    df.loc[mask,'name_max']=df[mask]['ipni_name_auth'].shift(-1)
    # Forward fill in gaps
    df['name_min']=df['name_min'].ffill()
    df['name_max']=df['name_max'].ffill()
    df['name_max']=df['name_max'].bfill()
    # Process window for the start of name list 
    # (as there will be no name_min for these entries)
    first_matched=list(df[df.ipni_name_auth.notnull()].ipni_name_auth)[0]
    mask=(df.clean_name.notnull())&(df.clean_name.apply(lambda x: len(str(x)) > 0 and str(x)<first_matched))
    df.loc[mask,'name_min']=None
    df.loc[mask,'name_max']=first_matched
    # Process window for the end of name list 
    # (as there will be no name_max for these entries)
    last_matched=list(df[df.ipni_name_auth.notnull()].ipni_name_auth)[-1]
    mask=(df.clean_name.notnull())&(df.clean_name.apply(lambda x: len(str(x)) > 0 and str(x)>last_matched))
    df.loc[mask,'name_min']=last_matched
    df.loc[mask,'name_max']=None

    # Ensure np.nan / None consistent
    df=df.where(df.notnull(), None)

    # Loop over unmatched entries
    for i,row in df[df['id'].isnull()&df['clean_name'].notnull()].iterrows():
        matched = False
        line_id = row['line_id']
        print(row['clean_name'],row['name_min'],row['name_max'])
        # Match strategy 1/2: match on first word only
        #print('Matching using: first word')
        first_word = row['clean_name'].split(' ')[0]
        is_fam = first_word.endswith('aceae')
        mask = dfn.ipni_name_auth.apply(lambda x: str(x).startswith(first_word))
        df_temp = pd.DataFrame(dfn[mask][['id','ipni_name_auth']])
        df_temp['similarity']=df_temp.ipni_name_auth.apply(lambda x: distance(x,row['clean_name']))
        if len(df_temp) > 0:
            matched = True
            best_id_1 = df_temp.sort_values(by='similarity',ascending=True).id.iloc[0]
            matched_name_1 = df_temp.sort_values(by='similarity',ascending=True).ipni_name_auth.iloc[0]
        else:
            best_id_1 = None
            matched_name_1 = None
        #print(df_temp.sort_values(by='similarity',ascending=True).head(n=3))

        # Match strategy 2/2: match using name window
        #print('Matching using: window')
        mask = None
        if row['name_min'] is not None:
            mask= (dfn.ipni_name_auth.apply(lambda x: (str(x) > row['name_min'])))
        if row['name_max'] is not None:
            max_mask = (dfn.ipni_name_auth.apply(lambda x: (str(x) < row['name_max'])))
            if mask is not None:
                mask = mask & max_mask
            else:
                mask = max_mask
        
        df_temp = pd.DataFrame(dfn[mask][['id','ipni_name_auth']])
        df_temp['similarity']=df_temp.ipni_name_auth.apply(lambda x: distance(x,row['clean_name']))
        if len(df_temp) > 0:
            matched = True
            best_id_2 = df_temp.sort_values(by='similarity',ascending=True).id.iloc[0]
            matched_name_2 = df_temp.sort_values(by='similarity',ascending=True).ipni_name_auth.iloc[0]
        else:
            best_id_2 = None
            matched_name_2 = None
        # TODO: select one
        if matched:
            if best_id_1 == best_id_2:
                df.loc[df.line_id==line_id,'id']=best_id_1
                df.loc[df.line_id==line_id,'ipni_name_auth']=matched_name_1
                df.loc[df.line_id==line_id,'match_stage']=1
            else:
                df.loc[df.line_id==line_id,'id']=best_id_2
                df.loc[df.line_id==line_id,'ipni_name_auth']=matched_name_2
                df.loc[df.line_id==line_id,'match_stage']=2
    output_cols=['filename','page_number','line_number','line_id','line','clean_name','ipni_name_auth','id','match_stage','name_min','name_max']
    df[output_cols].to_csv(outputfile,sep='\t',encoding='utf8',index=False)

if __name__ == '__main__':
    main()