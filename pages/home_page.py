from flask import Flask
import pandas as pd
import numpy as np
import os
import dash
from dash import Dash, html, dcc, Input, Output, dash_table, callback
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
from dash.exceptions import PreventUpdate

dash.register_page(__name__, path='/')

#app = Dash(__name__, server=server) # initiate the dashboard
# directories
cwd = os.getcwd() # directory this file is saved in
##data_dir = os.path.join(cwd, "BCDC-Metadata") # BCDC data folder
#metadata_dir = os.path.join(data_dir, 'Sample-Inventory') # directory with metadata

## sample/subject table
df_sample = pd.read_csv(os.path.join(cwd, 'dash_sample_count_df.csv'), encoding='unicode_escape')
df = pd.read_csv(os.path.join(cwd, 'dash_specimen_count_df.csv'), encoding='unicode_escape')
df['library_count'] = df['library_count'] + df['extra_library_count']


## sort the quarters for the plots in case they are not in order
# looks like they are for this particular csv
quarters = df['quarters'].unique()
sort_df = pd.DataFrame({'dates':quarters})['dates'].str.split('Q', expand = True)
sort_df.columns = ['year', 'quarter']
sort_df['date'] = quarters
quarter_order = sort_df.sort_values(['year', 'quarter'])['date'].unique()

# by years
df['years']= df['quarters'].str.split('Q').str[0]
df_sample['years']= df_sample['quarters'].str.split('Q').str[0]
year_order = sorted(df['years'].unique())

#subspecimen_count_selections = list(df.filter(like='count').columns)
mod_categories = ['by grant', 'by species', 'by project', 'by archive', 'by techniques']
donor_view_categories = ['Subject/Donors', 'Brain Counts', 'Cell Counts', 'Tissue Counts', 'Library Counts']
test_options = ['Modality', 'Species', 'Grant', 'Project', 'Technique', 'Archive', 'Years']
data_type_categories = ['Species', 'Archive', 'Modality', 'Grant', 'Technique']

visualization_types = ['Modalities', 'Deposition Counts', 'Custom View']
modality_choices = df['modality'].unique()

# lookup tables
col_lookup = {'by grant': 'grant_reference_id', 'by species': 'species', 'by project':'data_collection_reference_id', 'by archive':'archive', 'by techniques':'technique'}
axis_lookup = {'Modality':'modality', 'Species':'species', 'Grant': 'grant_reference_id', 'Project': 'data_collection_reference_id', 'Technique':'technique', 'Archive':'archive', 'Quarters':'quarters', 'Years':'years'}
metric_lookup = {'Subject/Donors':'donor_count', 'Brains':'brain_count', 'Cells':'cell_count', 'Tissue Samples':'tissue_region_count', 'Libraries':'library_count'}


### layout
layout = html.Div([
    html.H1(
        children='BICAN Data Dashboard - Home Page', style={'textAlign': 'center'}
    ),
    
    html.Label(['View'], style={'font-weight': 'bold', "text-align": "center"}),
        dcc.Dropdown(id='dtype_view',
            options = ['Grant', 'Species', 'Archive'],
            value = 'Grant', style={'width':'60%'}),

    html.Div(id='graph-output')
])


@callback(
    Output('graph-output', 'children'),
    Input('dtype_view', 'value'))
def update_main(dtype_view):
    dtype = axis_lookup[dtype_view]
    df_main = df.pivot_table(index=['modality', 'technique'], columns=dtype, values='data_collection_reference_id', aggfunc='first').notnull().astype('int').reset_index()
    df_main.loc[df_main['modality'].duplicated(), 'modality'] = '  '
    df_main = df_main.replace(to_replace = 0, value = '')

    table = go.Table(
        header = dict(values = df_main.columns.tolist(), font = dict(color = 'black', size = 11)),
        cells = dict(values = df_main.T, 
                        fill_color=np.select(
            [df_main.T.values == 1, df_main.T.values == ''],
            ["blue", "white"],
            "aliceblue"),
            line_color='darkslategray',
            font = dict(color = 'blue', size = 13)
            )
    )
    fig = go.Figure(data = table)
    
    fig.data[0]['columnwidth'] = [5, 7]+[1.5]*(len(df_main.columns)-2)
    return html.Div([
        dcc.Graph(figure = fig, style={'height': 1100, 'width': '100%', 'display':'block'})
    ])