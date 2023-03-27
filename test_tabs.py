from flask import Flask
import pandas as pd
import numpy as np
import os
from dash import Dash, html, dcc, Input, Output, Patch
import plotly.express as px
import plotly.graph_objects as go


server = Flask(__name__)

app = Dash(__name__, server=server) # initiate the dashboard
# directories
cwd = os.getcwd() # directory this file is saved in
##data_dir = os.path.join(cwd, "BCDC-Metadata") # BCDC data folder
#metadata_dir = os.path.join(data_dir, 'Sample-Inventory') # directory with metadata

## sample/subject table
df_sample = pd.read_csv(os.path.join(cwd, 'dash_sample_count_df.csv'), encoding='unicode_escape')
df = pd.read_csv(os.path.join(cwd, 'dash_specimen_count_df.csv'), encoding='unicode_escape')

## sort the quarters for the plots in case they are not in order
# looks like they are for this particular csv
quarters = df['quarters'].unique()
sort_df = pd.DataFrame({'dates':quarters})['dates'].str.split('Q', expand = True)
sort_df.columns = ['year', 'quarter']
sort_df['date'] = quarters
quarter_order = sort_df.sort_values(['year', 'quarter'])['date'].unique()

subspecimen_count_selections = list(df.filter(like='count').columns)

visualization_types = ['Modalities', 'Deposition Counts', 'Custom View']
modality_choices = df['modality'].unique()

app.layout = html.Div([
    html.H1(
        children='BICAN Data Dashboard - Draft', style={'textAlign': 'center'}
    ),
    
    dcc.Tabs(id="tabs", value='modalities', children=[
        dcc.Tab(label='Modality Views', value='modalities'),
        dcc.Tab(label='Deposition Counts', value='deposition', children=[
                dcc.RadioItems(id='specimen_name',
                    options = subspecimen_count_selections,
                    value = subspecimen_count_selections[0], inline= False)]),
        dcc.Tab(label = 'Sample/Donor Count', value = 'donor_count')
        
        ]),
    html.Div(id='graph-output')
])


@app.callback(
    Output('graph-output', 'children'),
    Input('tabs', 'value'),
    Input('specimen_name', 'value'))

def update_fig(tabs, specimen_name):
    if tabs == 'modalities':
        ## for imaging, look at the number of brains/tissue regions
        df_imaging = df[df['modality'] == 'imaging']
        df_imaging['sample_counts'] = df_imaging['brain_count'] + df_imaging['tissue_region_count']
        df_imaging = df_imaging.groupby(['quarters', 'grant_reference_id'], as_index= False)['sample_counts'].sum()
        fig1 = px.bar(df_imaging, x = 'quarters', y = 'sample_counts', color= 'grant_reference_id', title = 'Imaging')
        fig1.update_layout(xaxis_title = "Quarters", yaxis_title = 'Brains and Tissues Imaged')

        ## for anatomy, also look at number of brains/tissue regions
        df_anatomy = df[df['modality'] == 'anatomy/morphology']
        df_anatomy['sample_counts'] = df_anatomy['brain_count'] + df_anatomy['tissue_region_count']
        df_anatomy = df_anatomy.groupby(['quarters', 'grant_reference_id'], as_index=False)['sample_counts'].sum()
        fig2 = px.bar(df_anatomy, x = 'quarters', y = 'sample_counts', color= 'grant_reference_id', title= 'Anatomy/morphology')
        fig2.update_layout(xaxis_title = "Quarters", yaxis_title = 'Brains and Tissue Samples')

        ## for OMICs, count cells and libraries for now
        df_omics = df[df['modality'].str.contains('omics')]
        df_omics['sample_counts'] = df_omics['cell_count'] + df_omics['library_count']
        df_omics = df_omics.groupby(['quarters', 'grant_reference_id'], as_index=False)['sample_counts'].sum()
        fig3 = px.bar(df_omics, x = 'quarters', y = 'sample_counts', color= 'grant_reference_id', title = 'OMICs')
        fig3.update_layout(xaxis_title = "Quarters", yaxis_title = 'Cells and Libraries')
        
        ### neuron reconstructions
        df_recons = df[df['modality'] == 'cell morphology'].groupby(['quarters', 'grant_reference_id'], as_index= False)['cell_count'].sum()
        fig4 = px.bar(df_recons, x = 'quarters', y = 'cell_count', color= 'grant_reference_id', title = 'Cell Morpholohy - Neuron Reconstruction')
        fig4.update_layout(xaxis_title = "Quarters", yaxis_title = 'Cells reconstructed')

        ### multimodal - count cells (?)
        df_multimodal = df[df['modality'] == 'multimodal'].groupby(['quarters', 'grant_reference_id'], as_index= False)['cell_count'].sum()
        fig5 = px.bar(df_multimodal, x = 'quarters', y = 'cell_count', color= 'grant_reference_id', title = 'Multimodal')
        fig5.update_layout(xaxis_title = "Quarters", yaxis_title = 'Cells')

        return html.Div([
        dcc.Graph(figure = fig1, style={'height': 500, 'width': '30%', 'display':'inline-block'}),
        dcc.Graph(figure = fig2, style={'height': 500,'width': '30%', 'display':'inline-block'}),
        dcc.Graph(figure = fig3, style={'height': 500,'width': '30%', 'display':'inline-block'}),
        dcc.Graph(figure = fig4, style={'height': 500,'width': '30%', 'display':'inline-block'}),
        dcc.Graph(figure = fig5, style={'height': 500,'width': '30%', 'display':'inline-block'})
      ])
    
    elif tabs == 'deposition':
        fig = px.bar(df, x='quarters', y=specimen_name, color = 'data_collection_reference_id', height=700)
        fig.update_xaxes(categoryorder='array', categoryarray = quarter_order)
        fig.update_layout(xaxis_title = "Quarters", yaxis_title = 'Number of Specimens Processed')
        return html.Div([
            dcc.Graph(figure = fig, style={'height': 1000, 'width': '100%', 'display':'block'})
        ])
    
    elif tabs == 'donor_count':
        df_quarter_donor = df[['species', 'quarters', 'donor_count']].drop_duplicates()
        df_quarter_donor = pd.DataFrame(df_quarter_donor.drop_duplicates().groupby(['species', 'quarters'], as_index = False)['donor_count'].sum())
        fig = px.bar(df_quarter_donor, x='quarters', y='donor_count', color = 'species', height=700)
        fig.update_xaxes(categoryorder='array', categoryarray = quarter_order)
        fig.update_layout(xaxis_title = "Quarters", yaxis_title = 'Number of Subjects/Donors')

        return html.Div([
            dcc.Graph(figure = fig, style={'height': 1000, 'width': '100%', 'display':'block'})
        ])
        
## launch command
if __name__ == '__main__':
    app.run_server()


