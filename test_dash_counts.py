import pandas as pd
import numpy as np
import os, glob
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go


app = Dash(__name__) # initiate the dashboard
# directories
cwd = os.getcwd() # directory this file is saved in
##data_dir = os.path.join(cwd, "BCDC-Metadata") # BCDC data folder
#metadata_dir = os.path.join(data_dir, 'Sample-Inventory') # directory with metadata

df = pd.read_csv(os.path.join(cwd, 'dash_count_df.csv'), encoding='unicode_escape')

## sort the quarters for the plots in case they are not in order
# looks like they are for this particular csv
quarters = df['quarters'].unique()
sort_df = pd.DataFrame({'dates':quarters})['dates'].str.split('Q', expand = True)
sort_df.columns = ['year', 'quarter']
sort_df['date'] = quarters
quarter_order = sort_df.sort_values(['year', 'quarter'])['date'].unique()


visualization_types = ['Subject/Donor Counts', 'Specimen Counts']
subspecimen_count_selections = list(df.columns)[5:] # do not include project name as this is used for selection
categories = ['by grant', 'by quarter']

### dashboard layout
app.layout = html.Div([
    ## headers
    html.H1(children='Sample Count Dashboard - BCDC Metadata'),
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
        html.Div([
            #html.Label(['Category'], id = 'category_label', style={'font-weight': 'bold', "text-align": "center", 'display':'text'}),
            dcc.RadioItems(
                subspecimen_count_selections,
                subspecimen_count_selections[0],
                id='specimen_name')
                ], style={'width': '48%', 'display': 'block'}),
        html.Div([
            dcc.RadioItems(
                categories,
                categories[0],
                id='category')
                ], style={'width': '48%', 'display': 'block'})
    ]),
     
    ## graphs
    dcc.Graph(id='main_plot')
])

### main callbacks into the update_graph() function
@app.callback(
    Output('specimen_name', 'style'),
    Input('measure_type', 'value')) 
def show_hide(measure_type):
    if 'Specimen' in measure_type: # only show for count
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    # output - visualizations
    Output('main_plot', 'figure'),
    # input - variables from dropdown/selected values
    Input('measure_type', 'value'),
    Input('specimen_name', 'value'),
    Input('category', 'value')
)





def update_graph(measure_type, specimen_name, category):
    #print(df_test[df_test['subject'] > 1000])
    if 'Subject' in measure_type:
        if 'grant' in category:
            df_grant = df[['data_collection_reference_id', 'grant_reference_id', 'donor_count']].drop_duplicates()
            df_grant = pd.DataFrame(df_grant.drop_duplicates().groupby(['data_collection_reference_id', 'grant_reference_id'], as_index = False)['donor_count'].sum())
            fig = px.bar(df_grant, x='grant_reference_id', y='donor_count', color = 'data_collection_reference_id', height=700)
            fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
            return fig
        if 'quarter' in category:
            df_quarter_donor = df[['data_collection_reference_id', 'quarters', 'donor_count']].drop_duplicates()
            df_quarter_donor = pd.DataFrame(df_quarter_donor.drop_duplicates().groupby(['data_collection_reference_id', 'quarters'], as_index = False)['donor_count'].sum())
            fig = px.bar(df_quarter_donor, x='quarters', y='donor_count', color = 'data_collection_reference_id', height=700)
            fig.update_xaxes(categoryorder='array', categoryarray = quarter_order)
            return fig
    if 'Specimen' in measure_type:
        if 'grant' in category:
            df_grant = df[['data_collection_reference_id', 'grant_reference_id', specimen_name]]
            df_grant = pd.DataFrame(df_grant.groupby(['data_collection_reference_id', 'grant_reference_id'], as_index = False)['brain_count'].sum())
            fig = px.bar(df_grant, x='grant_reference_id', y=specimen_name, color = 'data_collection_reference_id', height=700)
            fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
            return fig
        if 'quarter' in category:
            fig = px.bar(df, x='quarters', y=specimen_name, color = 'data_collection_reference_id', height=700)
            fig.update_xaxes(categoryorder='array', categoryarray = quarter_order)
            return fig

        

    
## launch command
if __name__ == '__main__':
    app.run_server()



