import pandas as pd
import numpy as np
import os, glob
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import re
import dash_util 

app = Dash(__name__) # initiate the dashboard

cwd = os.getcwd() # current work directory
data_dir = os.path.join(cwd, "BCDC-Metadata", 'Sample-Inventory')

### Use only the newest data, which is the 2022Q3 - as that is cumulative
### read in the data for selected quarter
df_selected = pd.read_csv(os.path.join(data_dir, 'BCDC_Metadata_2022Q3.csv'), encoding='unicode_escape')
controlled_cols = [re.sub("\([^)]*\)", "", x).strip() for x in list(filter(lambda x : 'CV' in x, df_selected.columns))] ## map the values to controlled vocabs somehow

ontology_df = dash_util.get_lims2_ontology('Mouse.csv')
print(ontology_df)

## controlled vocab file
#cv_df = pd.read_csv(os.path.join(cwd, 'controlled_vocabs.csv'), encoding='unicode_escape').dropna(how='all', axis=1)

# clean up data columns, column had 'CV' control value labels which we do not need. 
    # It complicates the column selection process
df_selected.columns = df_selected.columns.str.replace(r"\([^)]*\)","").str.strip() # clean up data columns
df_selected['Sample Type'] = df_selected['Sample Type'].str.replace("[^A-Za-z0-9 ]+", " ").str.lower() # special characters into spaces
df_selected['Subspecimen Type'] = df_selected['Subspecimen Type'].str.replace("[^A-Za-z0-9 ]+", " ").str.lower() # special characters into spaces
df_selected['Total Processed Subspecimens'] = df_selected['Total Processed Subspecimens'].astype(str).str.replace(',', '').astype(float) # cell counts is numeric
df_selected['Species'] = df_selected['Species'].str.lower()

## sort the quarters for the plots in case they are not in order
# looks like they are for this particular csv
quarters = df_selected['Metadata Submission'].unique()
sort_df = pd.DataFrame({'dates':quarters})['dates'].str.split('Q', expand = True)
sort_df.columns = ['year', 'quarter']
sort_df['date'] = quarters
quarter_order = sort_df.sort_values(['year', 'quarter'])['date'].unique()

# required visualization types
visualization_types = ['Sample Counts', 'Increments']#, 'Custom']


panel_options = {
    'Sample Counts':['Number of File Uploads', 'Number of Cells', 'Number of Brains'],
    'Increments': ['Number of File Uploads', 'Number of Cells', 'Number of Brains']
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
                visualization_types,
                visualization_types[0],
                id='measure_type')
                ], style={'width': '48%'}),
        html.Br(), # some blank space
        ## second selection - by grant or quarter
        # conditionally show up
        html.Div([
            #html.Label(['Category'], id = 'category_label', style={'font-weight': 'bold', "text-align": "center", 'display':'text'}),
            dcc.RadioItems(
                ['by quarter', 'by grant'],
                'by quarter',
                id='category')
                ], style={'width': '48%', 'display': 'block'}),
        html.Br(),
        ## third selection - unit type for count
        ## static, always here
        ## only one at a time
        html.Div([
            #html.Label(['Unit Type'], id = 'unit_label', style={'font-weight': 'bold', "text-align": "center"}),
            dcc.RadioItems(
                id='unit_type')
                ], style={'width': '48%'}),
        html.Br(),
        ### fourth selection - detailed view type
        # conditionally show up
        html.Div([
            #html.Label(['Details'], id = 'detail_label', style={'font-weight': 'bold', "text-align": "center", 'display':'text'}),
            dcc.RadioItems(
                ['Cumulative', 'Species', 'Technique', 'Modality', "Data Collection", "R24 Name"],
                'Cumulative',
                id='detail_type')
                ], style={'width': '48%', 'display': 'block'})
        
        
        
    ]),
    ## graphs
    dcc.Graph(id='main_plot')
])

## function to get list of applicable units per measurement type  
@app.callback(
    Output('unit_type', 'options'),
    Input('measure_type', 'value'))
def set_subcat_options(measure_type):
    if 'Sample Counts' in measure_type or 'Increments' in measure_type:
        return panel_options[measure_type] # should give the according values in the dictionary

## function to get the units into values for function
@app.callback(
    Output('unit_type', 'value'),
    Input('unit_type', 'options'))
def set_unit_value(unit):
    #print(unit)
    return unit[0]

#### category, unit type, and details options are specific to counts
## so they only show up for that
### 1. category callback hide/show and its label
@app.callback(
    Output('category', 'style'),
    Input('measure_type', 'value')) 
def show_hide(measure_type):
    if 'Counts' in measure_type: # only show for count
        return {'display': 'block'}
    else:
        return {'display': 'none'}

### 3. show/hide detail groups
@app.callback(
    Output('detail_type', 'style'),
    Input('measure_type', 'value')) 
def show_hide(measure_type):
    if 'Counts' in measure_type: # only show for count
        return {'display': 'block'}
    else:
        return {'display': 'none'}


### main callbacks into the update_graph() function
@app.callback(
    # output - visualizations
    Output('main_plot', 'figure'),
    # input - variables from dropdown/selected values
    Input('measure_type', 'value'),
    Input('unit_type', 'value'),
    Input('category', 'value'), 
    Input('detail_type', 'value')
)

def update_graph(measure_type, unit_type, category, detail_type):
    # cell dataset
    df_cells = df_selected[(df_selected['Sample Type'].str.contains("cell", na = False)) | (df_selected['Subspecimen Type'].str.contains("cell", na = False))] # if either column says cells
    # brain dataset
    df_brains = df_selected[(df_selected['Sample Type'].str.contains("whole brain", na = False)) | (df_selected['Subspecimen Type'].str.contains("whole brain", na = False))] # if either column says brains
    df_brains = df_brains[~(df_brains['Parent Specimen Type'].str.contains("brain", na = False))]
    df_brains = df_brains[~(df_brains['Subspecimen Type'].str.contains("cell", na = False))]
    
    if 'Sample Counts' in measure_type:
        if 'quarter' in category:
            if 'Uploads' in unit_type:
                if detail_type == 'Cumulative':
                    df_q = pd.DataFrame({'count':df_selected.groupby(['Metadata Submission']).size()}).sort_values('count').reset_index()
                    q_fig = px.bar(df_q, x="Metadata Submission", y="count", text_auto=True,
                                title = "Number of Data Uploads per Quarter",
                                height=500, width= 1500)
                else:
                    df_q = pd.DataFrame({'count':df_selected.groupby(['Metadata Submission', detail_type]).size()}).sort_values('count').reset_index()
                    q_fig = px.bar(df_q, x="Metadata Submission", y="count", color = detail_type, text_auto=True,
                                title = "Number of Data Uploads per Quarter",
                                height=500, width= 1500)
                q_fig.update_layout(xaxis_title = "Quarter", yaxis_title = 'Sample Count')
                q_fig.update_xaxes(categoryorder='array', categoryarray = quarter_order)
                return q_fig
            if 'Cells' in unit_type:
                #df_cells = df_selected[(df_selected['Sample Type'].str.contains("cell", na = False)) | (df_selected['Subspecimen Type'].str.contains("cell", na = False))] # if either column says cells
                if detail_type == 'Cumulative':
                    df_cellcounts = pd.DataFrame({'cell_counts':df_cells.groupby(['Metadata Submission'])['Total Processed Subspecimens'].sum()}).sort_values('cell_counts').reset_index()
                    c_fig = px.bar(df_cellcounts, x="Metadata Submission", y="cell_counts", text_auto=True,
                                title = "Number of Cells Processed per Quarter",
                                height=500, width= 1500)
                else:
                    df_cellcounts = pd.DataFrame({'cell_counts':df_cells.groupby(['Metadata Submission', detail_type])['Total Processed Subspecimens'].sum()}).sort_values('cell_counts').reset_index()
                    c_fig = px.bar(df_cellcounts, x="Metadata Submission", y="cell_counts", color = detail_type, text_auto=True,
                                title = "Number of Cells Processed per Quarter",
                                height=500, width= 1500)
                c_fig.update_xaxes(categoryorder='array', categoryarray = quarter_order)
                #c_fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
                c_fig.update_layout(xaxis_title = "Quarter", yaxis_title = 'Cell Count')
                return c_fig
            if 'Brains' in unit_type:
                #df_brains = df_selected[(df_selected['Sample Type'].str.contains("whole brain", na = False)) | (df_selected['Subspecimen Type'].str.contains("whole brain", na = False))] # if either column says brains
                #df_brains = df_brains[~(df_brains['Parent Specimen Type'].str.contains("brain", na = False))]
                if detail_type == 'Cumulative':
                    df_braincounts = pd.DataFrame({'brain_counts':df_brains.groupby(['Metadata Submission'])['Total Processed Subspecimens'].sum()}).sort_values('brain_counts').reset_index()
                    b_fig = px.bar(df_braincounts, x="Metadata Submission", y="brain_counts", text_auto=True,
                                title = "Number of Brains Processed per Quarter",
                                height=500, width= 1500)
                else:
                    df_braincounts = pd.DataFrame({'brain_counts':df_brains.groupby(['Metadata Submission', detail_type])['Total Processed Subspecimens'].sum()}).sort_values('brain_counts').reset_index()
                    b_fig = px.bar(df_braincounts, x="Metadata Submission", y="brain_counts", color = detail_type, text_auto=True,
                                title = "Number of Brains Processed per Quarter",
                                height=500, width= 1500)
                b_fig.update_xaxes(categoryorder='array', categoryarray = quarter_order)
                b_fig.update_layout(xaxis_title = "Quarter", yaxis_title = 'Brain Count')
                return b_fig

        if 'grant' in category:
            if unit_type == 'Number of File Uploads':
                if detail_type == 'Cumulative':
                    df_g = pd.DataFrame({'count':df_selected.groupby(['Grant Number']).size()}).sort_values('count').reset_index()
                    g_fig = px.bar(df_g, x="Grant Number", y="count", text_auto=True,
                                title = "Number of Data Uploads Per Grant",
                                height=500, width= 1500)
                else:
                    df_g = pd.DataFrame({'count':df_selected.groupby(['Grant Number', detail_type]).size()}).sort_values('count').reset_index()
                    g_fig = px.bar(df_g, x="Grant Number", y="count", color = detail_type, text_auto=True,
                                title = "Number of Data Uploads Per Grant",
                                height=500, width= 1500)
                g_fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
                g_fig.update_layout(xaxis_title = "Grant Name", yaxis_title = 'Sample Count')
                return g_fig
            if 'Cells' in unit_type:
                #df_cells = df_selected[(df_selected['Sample Type'].str.contains("cell", na = False)) | (df_selected['Subspecimen Type'].str.contains("cell", na = False))] # if either column says cells
                if detail_type == 'Cumulative':    
                    df_cellcounts = pd.DataFrame({'cell_counts':df_cells.groupby(['Grant Number'])['Total Processed Subspecimens'].sum()}).sort_values('cell_counts').reset_index()
                    c_fig = px.bar(df_cellcounts, x="Grant Number", y="cell_counts", text_auto=True,
                            title = "Number of Cells Processed per Grant",
                            height=500, width= 1500)
                else:
                    df_cellcounts = pd.DataFrame({'cell_counts':df_cells.groupby(['Grant Number', detail_type])['Total Processed Subspecimens'].sum()}).sort_values('cell_counts').reset_index()
                    c_fig = px.bar(df_cellcounts, x="Grant Number", y="cell_counts", color = detail_type, text_auto=True,
                            title = "Number of Cells Processed per Grant",
                            height=500, width= 1500)
                c_fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
                c_fig.update_layout(xaxis_title = "Grant Name", yaxis_title = 'Cell Count')
                return c_fig
            if 'Brains' in unit_type:
                #df_brains = df_selected[(df_selected['Sample Type'].str.contains("whole brain", na = False)) | (df_selected['Subspecimen Type'].str.contains("whole brain", na = False))] # if either column says brains
                #df_brains = df_brains[~(df_brains['Parent Specimen Type'].str.contains("brain", na = False))]
                if detail_type == 'Cumulative':   
                    df_braincounts = pd.DataFrame({'brain_counts':df_brains.groupby(['Grant Number'])['Total Processed Subspecimens'].sum()}).sort_values('brain_counts').reset_index()
                    b_fig = px.bar(df_braincounts, x="Grant Number", y="brain_counts", text_auto=True,
                                title = "Number of Brains Processed per Grant",
                                height=500, width= 1500)
                else:
                    df_braincounts = pd.DataFrame({'brain_counts':df_brains.groupby(['Grant Number', detail_type])['Total Processed Subspecimens'].sum()}).sort_values('brain_counts').reset_index()
                    b_fig = px.bar(df_braincounts, x="Grant Number", y="brain_counts", color = detail_type, text_auto=True,
                                title = "Number of Brains Processed per Grant",
                                height=500, width= 1500)
                b_fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
                b_fig.update_layout(xaxis_title = "Grant", yaxis_title = 'Brain Count')
                return b_fig

    if 'Increments' in measure_type:
        if 'Uploads' in unit_type:
            count_inc = pd.DataFrame({'count':df_selected.groupby(['Metadata Submission']).size()}).sort_values('count').reset_index()
            count_inc['Metadata Submission'] = pd.Categorical(count_inc['Metadata Submission'], quarter_order)
            count_inc = count_inc.sort_values('Metadata Submission')
            diff_df = count_inc.set_index('Metadata Submission').diff().fillna(0)
            diff_df.reset_index(inplace = True)
            inc_fig = px.bar(diff_df, x="Metadata Submission", y="count", text_auto=True,
                                title = "Quarterly Increments of data deposition",
                                height=500, width= 1500)
            inc_fig.update_layout(xaxis_title = "quarter", yaxis_title = 'Data Deposition Count')
            return inc_fig
        if 'Cells' in unit_type:
            cell_inc = pd.DataFrame({'count':df_cells.groupby(['Metadata Submission'])['Total Processed Subspecimens'].sum()}).sort_values('count').reset_index()
            cell_inc['Metadata Submission'] = pd.Categorical(cell_inc['Metadata Submission'], quarter_order)
            cell_inc = cell_inc.sort_values('Metadata Submission')
            diff_df = cell_inc.set_index('Metadata Submission').diff().fillna(0)
            diff_df.reset_index(inplace = True)
            inc_fig = px.bar(diff_df, x="Metadata Submission", y="count", text_auto=True,
                                title = "Quarterly Increments of total processed cells",
                                height=500, width= 1500)
            inc_fig.update_layout(xaxis_title = "quarter", yaxis_title = 'Cell Count')
            return inc_fig
        if 'Brains' in unit_type:
            brain_inc = pd.DataFrame({'count':df_brains.groupby(['Metadata Submission'])['Total Processed Subspecimens'].sum()}).sort_values('count').reset_index()
            brain_inc['Metadata Submission'] = pd.Categorical(brain_inc['Metadata Submission'], quarter_order)
            brain_inc = brain_inc.sort_values('Metadata Submission')
            diff_df = brain_inc.set_index('Metadata Submission').diff().fillna(0)
            diff_df.reset_index(inplace = True)
            inc_fig = px.bar(diff_df, x="Metadata Submission", y="count", text_auto=True,
                                title = "Quarterly Increments of total processed cells",
                                height=500, width= 1500)
            inc_fig.update_layout(xaxis_title = "quarter", yaxis_title = 'Cell Count')
            return inc_fig


    
## launch command
if __name__ == '__main__':
    app.run_server()
