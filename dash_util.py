
import pandas as pd
import numpy as np
import os

def get_lims2_ontology(file):
    cwd = os.getcwd() # current work directory
    ontology_dir = os.path.join(cwd, 'ontology')
    ### Mouse Brain atlas file from http://lims2/structure_graphs
    ontology_df = pd.read_csv(os.path.join(ontology_dir, file), sep='delimiter', engine='python')
    cols = list(ontology_df.columns.str.split(',').tolist()[0])
    ontology_df = ontology_df.iloc[:,0].str.split(',', expand=True)
    ontology_df.iloc[:,9] = ontology_df.iloc[:,9:].replace('', np.nan).apply(lambda x: pd.Series(x.dropna().values), 1).iloc[:,0]
    ontology_df = ontology_df.iloc[:, 0:10]
    ontology_df.columns = cols

    #for level in mouse_ontology['st_level'].unique():

    return ontology_df