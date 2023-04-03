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


server = Flask(__name__)

app = Dash(__name__, server=server) # initiate the dashboard
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

visualization_types = ['Modalities', 'Deposition Counts', 'Custom View']
modality_choices = df['modality'].unique()

# lookup tables
col_lookup = {'by grant': 'grant_reference_id', 'by species': 'species', 'by project':'data_collection_reference_id', 'by archive':'archive', 'by techniques':'technique'}
axis_lookup = {'Modality':'modality', 'Species':'species', 'Grant': 'grant_reference_id', 'Project': 'data_collection_reference_id', 'Technique':'technique', 'Archive':'archive', 'Quarters':'quarters', 'Years':'years'}
metric_lookup = {'Subject/Donors':'donor_count', 'Brain Counts':'brain_count', 'Cell Counts':'cell_count', 'Tissue Counts':'tissue_region_count', 'Library Counts':'library_count'}

app.layout = html.Div([
    html.H1(
        children='BICAN Data Dashboard - NIH', style={'textAlign': 'center'}
    ),
    
    dcc.Tabs(id="tabs", value='data_types', children=[
        dcc.Tab(label = 'Data Types', value = 'data_types', children=[
            html.Label(['View'], style={'font-weight': 'bold', "text-align": "center"}),
                dcc.Dropdown(id='dtype_view',
                    options = ['Grant', 'Species', 'Archive'],
                    value = 'Grant', style={'width':'60%'})
        ]),

        dcc.Tab(label='Modality Views', value='modalities', children=[
                html.Br(),
                html.Label(['Color'], style={'font-weight': 'bold', "text-align": "center"}),
                dcc.Dropdown(id='specimen_name',
                    options = mod_categories,
                    value = mod_categories[0], style={'width':'50%'}),
                html.Label(['x-axis'], style={'font-weight': 'bold', "text-align": "center"}),
                dcc.RadioItems(id='x_axis',
                    options = ['Years', 'Quarters'],
                    value = 'Years', style={'width':'50%'})
                ]),
        
        dcc.Tab(label = 'Donor View', value = 'donor_count', children=[
                html.Label(['x-axis'], style={'font-weight': 'bold', "text-align": "center"}),
                dcc.RadioItems(id='x_selection', options=['Grant', 'Years'], value='Grant')]),

        
        dcc.Tab(label = 'Specimen Type view', value = 'test_view', children= [
                html.Br(),
                html.Label(['x-axis'], style={'font-weight': 'bold', "text-align": "center"}),
                dcc.Dropdown(id='xaxis_test',
                    options = test_options,
                    value = test_options[0], style={'width':'50%'}),
                html.Label(['colors'], style={'font-weight': 'bold', "text-align": "center"}),
                dcc.Dropdown(id='colors_test', value = test_options[1], style={'width':'50%'})    
        ])
        
        ]),
    html.Div(id='graph-output')
])

### update dropdown to not include itself
@app.callback(
    dash.dependencies.Output('colors_test', 'options'),
    [dash.dependencies.Input('xaxis_test', 'value')]
)
def update_second_dropdown(xaxis_test):
    new_options = [ele for ele in test_options if ele != xaxis_test]
    return new_options


## update main 
@app.callback(
    Output('graph-output', 'children'),
    Input('tabs', 'value'),
    Input('specimen_name', 'value'),
    Input('x_axis', 'value'),
    Input('xaxis_test', 'value'), 
    Input('colors_test', 'value'),
    Input('x_selection', 'value'), 
    Input('dtype_view', 'value'))

def update_fig(tabs, specimen_name, x_axis, xaxis_test, colors_test, x_selection, dtype_view):

    axis_val = axis_lookup[x_axis]
    col_name = col_lookup[specimen_name]

    if tabs == 'modalities':
        ## lookup columns        
        ## for imaging, look at the number of brains/tissue regions
        df_imaging = df[df['modality'] == 'imaging']
        df_imaging['sample_counts'] = df_imaging['brain_count'] + df_imaging['tissue_region_count']
        df_imaging = df_imaging.groupby([axis_val, col_name], as_index= False)['sample_counts'].sum()
        fig1 = px.bar(df_imaging, x = axis_val, y = 'sample_counts', color= col_name, title = 'Imaging')
        fig1.update_xaxes(categoryorder='array', categoryarray = quarter_order)
        fig1.update_layout(xaxis_title = "variable", yaxis_title = 'Brains and Tissues Imaged')

        ## for anatomy, also look at number of brains/tissue regions
        df_anatomy = df[df['modality'] == 'anatomy/morphology']

        df_anatomy['sample_counts'] = df_anatomy['brain_count'] + df_anatomy['tissue_region_count']
        df_anatomy = df_anatomy.groupby([axis_val, col_name], as_index=False)['sample_counts'].sum()
        fig2 = px.bar(df_anatomy, x = axis_val, y = 'sample_counts', color= col_name, title= 'Anatomy/morphology')
        fig2.update_xaxes(categoryorder='array', categoryarray = quarter_order)
        fig2.update_layout(xaxis_title = "variable", yaxis_title = 'Brains and Tissue Samples')

        ## for OMICs, count cells and libraries for now
        ## plot libraries , and cells as a line above
        df_omics = df[df['modality'].str.contains('omics')]
        df_omics_cells = df_omics.groupby([axis_val], as_index=False)['cell_count'].sum()
        # cell line
        omics_lib_ct = df_sample[df_sample['modality'].str.contains('omics')]
        omics_lib_ct = omics_lib_ct[omics_lib_ct['sample_type'] != 'cell nucleus'].groupby([axis_val, col_name], as_index=False)['sample_count'].sum()

        fig3 = make_subplots(specs=[[{"secondary_y": True}]])
        fig3 = px.bar(omics_lib_ct, x = axis_val, y = 'sample_count', color= col_name, title = 'OMICs <br>Bar: Library counts, Line: Cell counts')
        fig_line = px.line(df_omics_cells, x = axis_val, y = 'cell_count')
        fig_line.update_traces(yaxis = 'y2')
        fig_line.update_xaxes(categoryorder='array', categoryarray = omics_lib_ct[axis_val].unique())
        fig3.add_traces(fig_line.data).update_layout(yaxis2={"overlaying":"y", "side":"right"}, xaxis2 = {'tickmode':'sync'})
        fig3.update_xaxes(categoryorder='array', categoryarray = quarter_order)
        fig3.update_layout(legend=dict(x = 1.07), xaxis_title = "variable")
        fig3.update_yaxes(title_text='Libraries and tissue samples', secondary_y=False)
        fig3.update_yaxes(title_text="Cell Counts", secondary_y=True)
        
        ### neuron reconstructions
        df_recons = df[df['modality'] == 'cell morphology'].groupby([axis_val, col_name], as_index= False)['cell_count'].sum()
        fig4 = px.bar(df_recons, x = axis_val, y = 'cell_count', color= col_name, title = 'Cell Morpholohy - Neuron Reconstruction')
        fig4.update_xaxes(categoryorder='array', categoryarray = quarter_order)
        fig4.update_layout(xaxis_title = "variable", yaxis_title = 'Cells reconstructed')

        ### multimodal - count cells (?)
        df_multimodal = df[df['modality'] == 'multimodal'].groupby([axis_val, col_name], as_index= False)['cell_count'].sum()
        fig5 = px.bar(df_multimodal, x = axis_val, y = 'cell_count', color= col_name, title = 'Multimodal')
        fig5.update_xaxes(categoryorder='array', categoryarray = quarter_order)
        fig5.update_layout(xaxis_title = "variable", yaxis_title = 'Cells')

        ### transcriptomics - count cells
        df_transcript = df[df['modality'] == 'spatial transcriptomics'].groupby([axis_val, col_name], as_index= False)['cell_count'].sum() 
        fig6 = px.bar(df_transcript, x = axis_val, y = 'cell_count', color= col_name, title = 'Transcriptomics')
        fig6.update_xaxes(categoryorder='array', categoryarray = quarter_order)
        fig6.update_layout(xaxis_title = "variable", yaxis_title = 'Cells')

        return html.Div([
        dcc.Graph(figure = fig1, style={'height': 500, 'width': '30%', 'display':'inline-block'}),
        dcc.Graph(figure = fig2, style={'height': 500,'width': '30%', 'display':'inline-block'}),
        dcc.Graph(figure = fig3, style={'height': 500,'width': '30%', 'display':'inline-block'}),
        dcc.Graph(figure = fig4, style={'height': 500,'width': '30%', 'display':'inline-block'}),
        dcc.Graph(figure = fig5, style={'height': 500,'width': '30%', 'display':'inline-block'}),
        dcc.Graph(figure = fig6, style={'height': 500,'width': '30%', 'display':'inline-block'})
      ])


    elif tabs == 'donor_count':
        axis_val = axis_lookup[x_selection]
        df_quarter_donor = df[['species', axis_val, 'donor_count', 'modality']].drop_duplicates()

        df_quarter_donor = pd.DataFrame(df_quarter_donor.drop_duplicates().groupby(['species', axis_val, 'modality'], as_index = False)['donor_count'].sum())  
        print(df_quarter_donor)
       # print('original')
        if axis_val == 'years':
            df_quarter_donor = df_quarter_donor.groupby(['modality', 'species', 'years']).sum().groupby(['modality','species']).cumsum().reset_index()
            print(df_quarter_donor)

            fig = px.bar(df_quarter_donor, x=axis_val, y='donor_count', color = 'species', facet_col='modality')
            fig.update_xaxes(categoryorder='array', categoryarray = year_order)
            fig.update_layout(yaxis_title = 'Counts')
            fig.for_each_yaxis(lambda y: y.update(showticklabels=True,matches=None))
            fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1].capitalize()))
        else:
            df_quarter_donor = df_quarter_donor.sort_values(['donor_count'])
            print(df_quarter_donor)
            fig = px.bar(df_quarter_donor, x=axis_val, y='donor_count', color = 'species', facet_col='modality')
            fig.update_layout(yaxis_title = 'Donor Counts')
            fig.for_each_yaxis(lambda y: y.update(showticklabels=True,matches=None))
            fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1].capitalize()))
            fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})


        return html.Div([
            dcc.Graph(figure = fig, style={'height': 500, 'width': '100%', 'display':'block'})
        ])
    
    elif tabs == 'data_types':
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
    
    elif tabs == 'test_view':
        x_test = axis_lookup[xaxis_test]
        color_test = axis_lookup[colors_test]
        ## assign colors
        colors = dict(matplotlib.colors.cnames.items())
        hex_colors = tuple(colors.values())


        df_tests = df[['brain_count', 'cell_count','tissue_region_count', 'library_count', x_test, color_test]].groupby([x_test, color_test], as_index= False).agg({'brain_count':'sum','cell_count':'sum', 'tissue_region_count':'sum', 'library_count':'sum'})
        plot_df = pd.melt(df_tests, id_vars=[x_test,color_test],value_vars=['brain_count', 'cell_count', 'tissue_region_count', 'library_count'])
        print(plot_df)
        fig = px.bar(plot_df, x=x_test, y='value', color = color_test, facet_col='variable')
        fig.for_each_yaxis(lambda y: y.update(showticklabels=True,matches=None))
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1].replace('_', ' ').capitalize()))

            # fig.update_layout(
            #     template="simple_white",
            #     xaxis=dict(title_text="Modality"),
            #     yaxis=dict(title_text="Count"),
            #     barmode="stack",
            # )

            # for r, c in zip(df_tests[color_test].unique(), hex_colors):
            #     plot_df = df_tests[df_tests[color_test] == r]
            #     plot_df = pd.melt(plot_df, id_vars=['modality',color_test],value_vars=['brain_count', 'cell_count'])
            #     #plot_brains = plot_df[['modality', color_test, 'value']]
            #     #print(plot_brains)
            #     fig.add_trace(
            #         go.Bar(x=plot_df.modality, y=plot_df.value, facet_col = 'variable', name=r, marker_color=c),
            #     )

            # color_pal = dict(zip())
            # print(df_tests)
            # #print(df_tests)
            # fig = go.Figure(
            #     data=[
            #         go.Bar(name = 'Brains', x=df_tests[x_test], y=df_tests['brain_count'], yaxis='y', offsetgroup=1),
            #         go.Bar(name='Cells', x=df_tests[x_test], y=df_tests['cell_count'], yaxis='y2', offsetgroup=2)
            #     ],
            #     layout={
            #         'yaxis': {'title': 'Brains'},
            #         'yaxis2': {'title': 'Cells', 'overlaying': 'y', 'side': 'right'}
            #     }
            # )

            # # Change the bar mode
            # fig.update_layout(barmode='group')


            #fig = px.bar(df_tests, x = test_view, y = ['brain_count', 'cell_count'], barmode='group')
        return html.Div([
            dcc.Graph(figure = fig, style={'height': 800, 'width': '100%', 'display':'block'})
        ])
       # if 'metrics_test' == 'donors':



## launch command
if __name__ == '__main__':
    app.run_server()


