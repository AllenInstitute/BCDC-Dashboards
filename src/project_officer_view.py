from flask import Flask
import pandas as pd
import numpy as np
import os
import dash
from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib
import webbrowser
from dash.exceptions import PreventUpdate


server = Flask(__name__)

app = Dash(__name__, server=server) # initiate the dashboard
# directories
cwd = os.path.dirname(os.getcwd()) # directory this file is saved in
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
metric_lookup = {'Subject/Donors':'donor_count', 'Brain Counts':'brain_count', 'Cell Counts':'cell_count', 'Tissue Counts':'tissue_region_count', 'Library Counts':'library_count'}

### URL lookup tables
archive_lookup = {'BIL':'https://www.brainimagelibrary.org/', 'DANDI':'https://dandiarchive.org/', 'NEMO': 'https://nemoarchive.org/'}
species_lookup = {'humans': 'https://dev-knowledge.brain-map.org/data?filter.species.name=CONTAINS~human&limit=25&offset=0&sort=species.name~ASC', 
                  'mouse':'https://dev-knowledge.brain-map.org/data?filter.species.name=CONTAINS~mouse&limit=25&offset=0&sort=species.name~ASC',
                  'non-human primates':'https://dev-knowledge.brain-map.org/data?filter.species.name=CONTAINS~Ma%27s%20night%20monkey,CONTAINS~chimpanzee,CONTAINS~green%20monkey,CONTAINS~squirrel%20monkey,CONTAINS~western%20gorilla&limit=25&offset=0&sort=species.name~ASC',
                  'other mammals':'https://dev-knowledge.brain-map.org/data?filter.species.name=CONTAINS~Norway%20rat,CONTAINS~chimpanzee,CONTAINS~gray%20short-tailed%20opossum,CONTAINS~marmoset,CONTAINS~pig,CONTAINS~pig-tailed%20macaque,CONTAINS~rabbit&limit=25&offset=0&sort=species.name~ASC'}
modality_lookup = {'anatomy/morphology': 'https://dev-knowledge.brain-map.org/data?filter.modality.name=CONTAINS~anatomy,CONTAINS~cell%20morphology,CONTAINS~histology%20imaging&limit=25&offset=0&sort=species.name~ASC',
                   'epigenomics': 'https://dev-knowledge.brain-map.org/data?filter.modality.name=CONTAINS~epigenomics&limit=25&offset=0&sort=species.name~ASC',
                   'imaging':'https://dev-knowledge.brain-map.org/data?filter.modality.name=CONTAINS~population%20imaging&limit=25&offset=0&sort=species.name~ASC',
                   'multimodal' :'https://dev-knowledge.brain-map.org/data?filter.modality.name=CONTAINS~electrophysiology,CONTAINS~multimodal&limit=25&offset=0&sort=species.name~ASC',
                   'spatial transcriptomics':'https://dev-knowledge.brain-map.org/data?filter.modality.name=CONTAINS~spatial%20transcriptomics&limit=25&offset=0&sort=species.name~ASC',
                   'transcriptomics/epigenomics': 'https://dev-knowledge.brain-map.org/data?filter.modality.name=CONTAINS~transcriptomics&limit=25&offset=0&sort=species.name~ASC',
                   'cell morphology':'https://dev-knowledge.brain-map.org/data?filter.modality.name=CONTAINS~cell%20morphology&limit=25&offset=0&sort=species.name~ASC'
}


### layout
app.layout = html.Div([
    html.H1(
        children='BICAN Data Dashboard - Project View', style={'textAlign': 'center'}
    ),
    
    dcc.Tabs(id="tabs", value='data_types', children=[
        dcc.Tab(label = 'Data Types', value = 'data_types', children=[
            html.Label(['View'], style={'font-weight': 'bold', "text-align": "center"}),
                dcc.Dropdown(id='dtype_view',
                    options = ['Grant', 'Species', 'Archive'],
                    value = 'Grant', style={'width':'60%'})
        ]),
        
        dcc.Tab(label = 'Sample Count', value = 'sample_count', children=[
                html.Label(['Category'], style={'font-weight': 'bold', "text-align": "center"}),
                dcc.Dropdown(id='sample_category',
                    options = data_type_categories,
                    value = 'Modality', style={'width':'60%'}),
                html.Label(['Color'], style={'font-weight': 'bold', "text-align": "center"}),
                dcc.Dropdown(id = 'category_color', value = 'Archive', style={'width':'60%'}),
                html.Br(),
                html.Div(children='''
                Click on each color bar to access the according URL link - function not available for 'Color = Grant'
                '''),
                ])
        
        ]),
    html.Div(id='graph-output')
])

### update dropdown to not include itself
@app.callback(
    dash.dependencies.Output('category_color', 'options'),
    [dash.dependencies.Input('sample_category', 'value')]
)
def update_second_dropdown(xaxis_test):
    new_options = [ele for ele in data_type_categories if ele != 'Technique']
    new_options = [ele for ele in new_options if ele != xaxis_test]
    return new_options



@app.callback(
   Output('data', 'children'),
   Input('interactive', 'clickData'))
def open_url(clickData):
   if clickData:
        webbrowser.open(clickData["points"][0]["customdata"][0])
   else:
        raise PreventUpdate


@app.callback(
    Output('graph-output', 'children'),
    Input('tabs', 'value'),
    Input('sample_category', 'value'),
    Input('dtype_view', 'value'),
    Input('category_color', 'value'))
def update_main(tabs, sample_category, dtype_view, category_color):
    if tabs == 'data_types':
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

    if tabs == 'sample_count':
        selected_category = axis_lookup[sample_category]
        selected_color = axis_lookup[category_color]
        plot_df = df_sample[[selected_category, 'sample_count', selected_color]].groupby([selected_category, selected_color], as_index= False)['sample_count'].sum()
        if selected_color == 'archive':
            plot_df['urls'] = plot_df['archive'].map(archive_lookup)
        elif selected_color == 'species':
            plot_df['urls'] = plot_df['species'].map(species_lookup)
        elif selected_color == 'modality':
            plot_df['urls'] = plot_df['modality'].map(modality_lookup)
        else:
            plot_df['urls'] = ''
        fig = px.bar(plot_df, x='sample_count', y=selected_category, color = selected_color, custom_data=['urls'], orientation='h')
        fig.update_layout(barmode='stack', yaxis={'categoryorder':'total ascending'})
        fig.update_layout(xaxis_title = "Sample Count", yaxis_title = sample_category)
        fig.update_layout(clickmode='event+select')


        return html.Div([
            dcc.Graph(id = 'interactive', figure=fig, style={'height': 500, 'width': '100%', 'display':'block'}),
            html.Pre(id='data')])
    



## launch command
if __name__ == '__main__':
    app.run_server()



