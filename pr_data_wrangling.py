import polars as pl
import pandas as pd
import numpy as np
import os, glob
import re
import plotly.express as px
import polars as pl

# directories
cwd = os.getcwd() # directory this file is saved in
data_dir = os.path.join(cwd, "BCDC-Metadata") # BCDC data folder
metadata_dir = os.path.join(data_dir, 'Sample-Inventory') # directory with specimen metadata
project_dir = os.path.join(data_dir, 'Data-Collection-Inventory', '2022Q3_csvs')

# using the data cleaned by Pam, which is stored separately in the current wd
df = pd.read_csv(os.path.join(cwd, 'BCDC_Metadata_2022Q3_v4.csv'), encoding='unicode_escape')

# clean up data and columns
df.columns = df.columns.str.replace(r"\([^)]*\)","").str.strip() # get rid of (CV) in data columns
df['Sample Type'] = df['Sample Type'].str.replace("[^A-Za-z0-9 ]+", " ").str.lower() # special characters into spaces, set all to lower - shouldn't have special characters in sample type
df['Species'] = df['Species'].str.lower() # species could be converted to all lowercase as well
df['Subspecimen Type'] = df['Subspecimen Type'].str.replace("[^A-Za-z0-9 ]+", " ").str.lower() # special characters into spaces, all lowercase
df['Total Processed Subspecimens'] = df['Total Processed Subspecimens'].astype(str).str.replace(',', '').astype(float) # cell counts is numeric
df['Sample ID'] = df['Sample ID'].astype(str) # so that IDs with all strings won't somehow get counted as numerics down the road
df['Species'] = df['Species'].str.lower()
df['Modality'] = df['Modality'].str.lower()
# if either sample type of subspecimen type is NA, use the other column
df['Sample Type'] = df['Sample Type'].fillna(df['Subspecimen Type'])
df['Subspecimen Type'] = df['Subspecimen Type'].fillna(df['Sample Type'])
# if no reported specimens, count as 0
df['Total Processed Subspecimens'] = df['Total Processed Subspecimens'].fillna(0)
### some columns are not getting considered at moment
optional_cols = ['Age', 'Sex', 'Genotype', 'Species NCBI Taxonomy ID']
df = df.drop(optional_cols, axis = 1)
df = df.drop_duplicates()

# fix the mc seq issue 
df.loc[(df['Technique'].str.contains('mc-seq', case = False)) & (~df['Technique'].str.contains(';', case = False)), 'Technique'] = 'mC-seq2'

#### Count for number of samples per categories
## implemented 'species' as a category for now, more to be added
sample_count_df = pd.DataFrame(df.groupby(['Data Collection', 'Metadata Submission', 'Species'], as_index = False).agg({'Sample ID': 'nunique'})).rename(columns = {'Data Collection':'data_collection_reference_id', 'Sample ID':'sample_count', 'Metadata Submission':'quarters', 'Sample Type': 'sample_name', 'Species':'species'})
## to-do: import these dictionaries from a different file, or integrate with ontologies
species_map = {
    'primates' : ['chimpanzee', 'small-eared galago', 'western gorilla', 'green monkey', 'pig-tailed macaque',
                 "ma's night monkey", 'rhesus macaque', 'bolivian squirrel monkey',
       'crab-eating macaque'],
    'humans' : ['human'], ## mostly mice and humans
    'mice' : ['mouse'],
    'marmoset': ['marmoset'],
    'small mammals': [
    'arctic ground squirrel',
    'nine-banded armadillo',
    'domestic cat',
    'domestic ferret',
    'gray short-tailed opossum',
    'pig', 'rabbit', 'norway rat', 'common tree shrew'
    ]
}

# map species column to the dictionary
sample_count_df['species'] = sample_count_df['species'].apply(lambda i:[k for k, v in species_map.items() if i in v]).str[0] 
# calculate new sum in collapsed group
sample_count_df = sample_count_df.groupby(['data_collection_reference_id', 'quarters', 'species'], as_index = False)['sample_count'].sum()

## output for dashboard
sample_count_df.to_csv(os.path.join(cwd, 'dash_sample_count_df.csv'), index = False)


#### Count for number of processed subspecimens
## get number of donors per quarter
# calculating donors here instead of above as it could potentially serve as a placeholder if brain count is misisng for brain-related techniques - one donor could count as one brain
df_donors = df.groupby(['Data Collection', 'Metadata Submission', 'Species'], as_index = False).agg({'Subject ID':'nunique'}).rename(columns = {'Data Collection':'data_collection_reference_id', 'Metadata Submission': 'quarters', 'Subject ID': 'donor_count', 'Species':'species'})
## get number of processed subspeciemns for each unique sample
df_subspecimens = df.groupby(['Data Collection', 'Metadata Submission', 'Sample ID', 'Subspecimen Type'], as_index = False).agg({'Total Processed Subspecimens':'sum'}).drop('Sample ID', axis = 1).rename(columns = {'Data Collection':'data_collection_reference_id', 'Metadata Submission': 'quarters', 'Subspecimen Type': 'subspecimen_type', 'Total Processed Subspecimens': 'subspecimen_count'})
# merge together
df_donor_counts = df_donors.merge(df_subspecimens, on = ['data_collection_reference_id', 'quarters'])
# grant/data collection lookup table so that grant names can be mapped to according projects
key_df = pd.read_csv(os.path.join(project_dir, 'data_collection_is_specified_output_of_data_collection_project.csv')).drop('priority_order', axis = 1)
grant_df = pd.read_csv(os.path.join(project_dir, 'grant_is_specified_input_of_data_collection_project.csv')).drop('priority_order', axis = 1)
metadata_df = grant_df.merge(key_df, on = 'project_reference_id', how = 'outer')[['data_collection_reference_id', 'grant_reference_id']]
df_donor_counts = metadata_df.merge(df_donor_counts, on = 'data_collection_reference_id', how = 'right')
# collapse species 
df_donor_counts['species'] = df_donor_counts['species'].apply(lambda i:[k for k, v in species_map.items() if i in v]).str[0]


## triage the projects funded by multiple grants situation and label those as 'multi'
# might do the same for projects reporting muiltiple techniques/species/modalities also, triaging for today's push
## projects funded by multiple grants
dup_df = df_donor_counts[['data_collection_reference_id', 'grant_reference_id']].drop_duplicates()
dup_count = pd.DataFrame(dup_df.drop_duplicates().groupby('data_collection_reference_id', as_index = False)['grant_reference_id'].nunique())
multi_list = dup_count[dup_count['grant_reference_id'] > 1]['data_collection_reference_id']
df_donor_counts.loc[df_donor_counts['data_collection_reference_id'].isin(multi_list), 'grant_reference_id'] = 'multi-grant'
## projects reporting multiple species
dup_df = df_donor_counts[['data_collection_reference_id', 'species']].drop_duplicates()
dup_count = pd.DataFrame(dup_df.drop_duplicates().groupby('data_collection_reference_id', as_index = False)['species'].nunique())
multi_list = dup_count[dup_count['species'] > 1]['data_collection_reference_id']
df_donor_counts.loc[df_donor_counts['data_collection_reference_id'].isin(multi_list), 'species'] = 'multi-species'


### dictionary to collapse the subspecimens
## techniques/modalities/species will be collapsed in a similar manner until this gets integrated with ontology at a future date TBD
specimen_count_map = {
'brain_count' : ['whole brain',
            'brain', 'brains'], # fix the plural
'cell_count' : ['whole cell', 
           'cell', 'cells', 'cell body', 'cell nucleus', 'nuclei', 'reconstruction', 'cell in slice'],
'nucleus_count' : ['cell nucleus', 'nuclei'],
'library_count' : ['library'],
'tissue_region_count' : ['brain hemisphere', 
                    'brain region', 
                    'brain section set', 
                    'brain slice', 
                    'library', 
                    'spinal cord slice',
                    'tissue sample',
                    'cell suspension']
}
    
    
## collapse using dictionary  
count_df = pd.DataFrame() # container to store
    
# for each project
for project in df_donor_counts['data_collection_reference_id'].unique():
    # list of column names to keep
    non_count_cols = ['data_collection_reference_id', 'grant_reference_id', 'quarters', 'species', 'donor_count', 'subspecimen_type']
    # use the above column names and the dictionary keys together as column names of the count dataframe
    count_df_project = pd.DataFrame(columns = [non_count_cols + list(specimen_count_map.keys())], index = [0])

    project_df = df_donor_counts[df_donor_counts['data_collection_reference_id'] == project]
    # if there are rows with same information, but different counts, sum those counts
    project_df = project_df.groupby(non_count_cols, as_index = False)['subspecimen_count'].sum() 

    ## for each quarter
    # could potentially write this into a function
    for i in range(len(project_df)):
        project_row = project_df.iloc[i]
        row_container = pd.DataFrame(columns = [non_count_cols + list(specimen_count_map.keys())], index = [0]) # another container
        #row_container[non_count_cols] = project_row[non_count_cols].drop('subspecimen_type')
        # copy the metadata
        row_container[['data_collection_reference_id', 'grant_reference_id', 'quarters', 'species', 'donor_count']] = project_row[['data_collection_reference_id', 'grant_reference_id', 'quarters', 'species', 'donor_count']]
        # get the categories to count, based on the dictionary
        count_cols = [k for k, v in specimen_count_map.items() if project_row['subspecimen_type'] in v]
        # update the according column
        row_container[count_cols] = project_row['subspecimen_count']
        # concat to container
        count_df_project = pd.concat([count_df_project, row_container.fillna(0)])
    
    count_df_project = count_df_project.dropna(how = 'all')
    count_df = pd.concat([count_df, count_df_project])

## output as csv for dashboard input
count_df.to_csv(os.path.join(cwd, 'dash_count_df.csv'), index = False)