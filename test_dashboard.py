import pandas as pd
import numpy as np
import os, glob
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import re

app = Dash(__name__) # initiate the dashboard

cwd = os.getcwd() # current work directory
data_dir = os.path.join(cwd, "BCDC-Metadata", 'Sample-Inventory')

### Use only the newest data, which is the 2022Q3 - as that is cumulative
### read in the data for selected quarter
df_selected = pd.read_csv(os.path.join(data_dir, 'BCDC_Metadata_2022Q3.csv'), encoding='unicode_escape')
controlled_cols = [re.sub("\([^)]*\)", "", x).strip() for x in list(filter(lambda x : 'CV' in x, df_selected.columns))] ## map the values to controlled vocabs somehow

# clean up data columns, column had 'CV' control value labels which we do not need. 
    # It complicates the column selection process
df_selected.columns = df_selected.columns.str.replace(r"\([^)]*\)","").str.strip() # clean up data columns
df_selected['Sample Type'] = df_selected['Sample Type'].str.replace("[^A-Za-z0-9 ]+", " ").str.lower() # special characters into spaces
df_selected['Subspecimen Type'] = df_selected['Subspecimen Type'].str.replace("[^A-Za-z0-9 ]+", " ").str.lower() # special characters into spaces
df_selected['Total Processed Subspecimens'] = df_selected['Total Processed Subspecimens'].astype(str).str.replace(',', '').astype(float) # cell counts is numeric


quarters = df_selected['Metadata Submission'].unique()

# required visualization types
visualization_types = ['Sample Counts']


panel_options = {
    'Sample Counts':['Number of File Uploads', 'Number of Cells', 'Number of Brains']
}


### dashboard layout
app.layout = html.Div([
    ## headers
    html.H1(children='Sample Dashboard - BCDC Metadata'),
    html.Div(children='''
       The data used for analysis was retrieved from the BCDC-Metadata repo. It only includes the Metadata files in the 'Sample-Inventory' directory for the time being.
    '''),
    html.Div(children='''
    Only using the 2022Q3 data - BCDC_Metadata_2022Q3.csv as it contains cumulative data for the previous quarters.
     '''),
    html.Div(children='''
    link to repository: https://github.com/BICCN/BCDC-Metadata/tree/BCDC-schema-v2/Sample-Inventory
     '''),
    html.Br(),

    ## dropdowns 
    html.Div([
        ## first dropdown - select Measure type (count, etc.)
        ### always here, no conditions
        html.Div([
            html.Label(['Measure Type'], style={'font-weight': 'bold', "text-align": "center"}),
            dcc.Dropdown(
                list(panel_options.keys()),
                list(panel_options.keys())[0],
                id='measure_type')
                ], style={'width': '48%'}),
        html.Br(), # some blank space
        ## second selection - by grant or quarter
        html.Div([
            html.Label(['Category'], style={'font-weight': 'bold', "text-align": "center"}),
            dcc.RadioItems(
                ['by quarter', 'by grant'],
                'by quarter',
                id='category')
                ], style={'width': '48%', 'display': 'block'}),
        html.Br(),
        ## third selection - unit type for count
        ## only show up for counts, set conditions in callbacks
        ## only one at a time
        html.Div([
            html.Label(['Unit Type'], style={'font-weight': 'bold', "text-align": "center"}),
            dcc.RadioItems(
                id='unit_type')
                ], style={'width': '48%', 'display': 'block'}),
        
        
        
    ]),
    ## graphs
    dcc.Graph(id='main_plot')
])

## function to get list of applicable units per measurement type  
@app.callback(
    Output('unit_type', 'options'),
    Input('measure_type', 'value'))
def set_subcat_options(measure_type):
    if 'Sample Counts' in measure_type:
        return panel_options[measure_type] # should give the according values in the dictionary

## function to get the units into values for function
@app.callback(
    Output('unit_type', 'value'),
    Input('unit_type', 'options'))
def set_unit_value(unit):
    return unit[0]

### main callbacks into the update_graph() function
@app.callback(
    # output - visualizations
    Output('main_plot', 'figure'),
    # input - variables from dropdown/selected values
    Input('measure_type', 'value'),
    Input('unit_type', 'value'),
    Input('category', 'value')
)

def update_graph(measure_type, unit_type, category):
    if 'Sample Counts' in measure_type:
        if 'quarter' in category:
            if 'Uploads' in unit_type:
                print('true')
                df_q = pd.DataFrame({'count':df_selected.groupby(['Metadata Submission']).size()}).sort_values('count').reset_index()
                q_fig = px.bar(df_q, x="Metadata Submission", y="count", text_auto=True,
                            title = "Number of Data Uploads per Quarter",
                            height=700, width= 1800)
                q_fig.update_layout(xaxis_title = "Quarter", yaxis_title = 'Sample Count')
                return q_fig
            if 'Cells' in unit_type:
                df_cells = df_selected[(df_selected['Sample Type'].str.contains("cell", na = False)) | (df_selected['Subspecimen Type'].str.contains("cell", na = False))] # if either column says cells
                df_cellcounts = pd.DataFrame({'cell_counts':df_cells.groupby(['Metadata Submission'])['Total Processed Subspecimens'].sum()}).sort_values('cell_counts').reset_index()
                c_fig = px.bar(df_cellcounts, x="Metadata Submission", y="cell_counts", text_auto=True,
                            title = "Number of Cells Processed per Quarter",
                            height=700, width= 1800)
                c_fig.update_layout(xaxis_title = "Quarter", yaxis_title = 'Cell Count')
                return c_fig
            if 'Brains' in unit_type:
                df_brains = df_selected[(df_selected['Sample Type'].str.contains("brain", na = False)) | (df_selected['Subspecimen Type'].str.contains("brain", na = False))] # if either column says brains
                df_braincounts = pd.DataFrame({'brain_counts':df_brains.groupby(['Metadata Submission'])['Total Processed Subspecimens'].sum()}).sort_values('brain_counts').reset_index()
                b_fig = px.bar(df_braincounts, x="Metadata Submission", y="brain_counts", text_auto=True,
                            title = "Number of Brains Processed per Quarter",
                            height=700, width= 1800)
                b_fig.update_layout(xaxis_title = "Quarter", yaxis_title = 'Brain Count')
                return b_fig

        if 'grant' in category:
            if unit_type == 'Number of File Uploads':
                df_g = pd.DataFrame({'count':df_selected.groupby(['Grant Number']).size()}).sort_values('count').reset_index()
                g_fig = px.bar(df_g, x="Grant Number", y="count", text_auto=True,
                            title = "Number of Data Uploads Per Grant",
                            height=700, width= 1800)
                g_fig.update_layout(xaxis_title = "Grant Name", yaxis_title = 'Sample Count')
                return g_fig
            if 'Cells' in unit_type:
                df_cells = df_selected[(df_selected['Sample Type'].str.contains("cell", na = False)) | (df_selected['Subspecimen Type'].str.contains("cell", na = False))] # if either column says cells
                df_cellcounts = pd.DataFrame({'cell_counts':df_cells.groupby(['Grant Number'])['Total Processed Subspecimens'].sum()}).sort_values('cell_counts').reset_index()
                c_fig = px.bar(df_cellcounts, x="Grant Number", y="cell_counts", text_auto=True,
                            title = "Number of Cells Processed per Grant",
                            height=700, width= 1800)
                c_fig.update_layout(xaxis_title = "Grant Name", yaxis_title = 'Cell Count')
                return c_fig
            if 'Brains' in unit_type:
                df_brains = df_selected[(df_selected['Sample Type'].str.contains("brain", na = False)) | (df_selected['Subspecimen Type'].str.contains("brain", na = False))] # if either column says brains
                df_braincounts = pd.DataFrame({'brain_counts':df_brains.groupby(['Grant Number'])['Total Processed Subspecimens'].sum()}).sort_values('brain_counts').reset_index()
                b_fig = px.bar(df_braincounts, x="Grant Number", y="brain_counts", text_auto=True,
                            title = "Number of Brains Processed per Grant",
                            height=700, width= 1800)
                b_fig.update_layout(xaxis_title = "Grant", yaxis_title = 'Brain Count')
                return b_fig

    
## launch command
if __name__ == '__main__':
    app.run_server()
