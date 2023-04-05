# BCDC-Dashboards
This repository is intended to store the codes for the BICAN dashboard, which takes the BCDC-Metadata repository as the input, performs data wrangling and launches the dashboard app script. The current version is a demo version that lives in the local environment and has not been integrated with the other pipelines yet, hence, the code structures are subject to change once the integration with the rest of the existing pipelines (i.e. databases, ontologies) happens.

### Installation (as of Apr 5, use the scripts in the dev branch)
#### Only works with python 64-bit
1. Clone repository, navigate to cloned directory in command line 
```cd BCDC-Dashboards```
2. switch to dev branch 
```git checkout dev```
3. start a virtual environment to avoid package version conflicts with 
```python3 -m venv env1```
'env1' is the name of the virtual environment which can be replaced with other names of your choice
4. activate virtual environment
```source env1/bin/activate```
5. install all requirements
```pip install -r requirements.txt```
6. ```cd src```
7. launch dashboard
```python3 ./NIH_view.py``` or ```python3 ./project_officer_view.py```

to-do: launch script that launches both dashboards

### Workflow
1. Input: BCDC-Metadata
2. Data Wrangling: dashboard_data_wrangling.ipynb
    Output: dash_count_df.csv
3. Dashboard script: test_tabs.py (takes dash_count_df.csv as input)
    Output: Dashboard page with visualizations

### Business logics:

The current dashboard allows the views of specimen counts, data depositions, and donor/subject counts by different categories. Detailed categories can be viewed in the dictionary file.

While counting, the groups and categories will be collapsed into similar terminologies to reduce the complexity of the plots so that they are more readable, and the grouping will be done primarily for sample types, specimen types, species, techniques, and modalities. It is expected that this pipeline will be connected with external taxonomy/ontology hierarchies to determine the most interoperable way of collapsing the terminologies.

[dashboard_logic_components.pdf](https://github.com/AllenInstitute/BCDC-Dashboards/files/11044153/dashboard_logic_components.pdf)

There are three panels in the dashboard:
1. Specimen counts by modality:
    a. For 'imaging' and 'anatomy', count the number of brains and tissues samples processed.
    b. For OMICs data, count the number of cells and libraries processed.
    c. For neuron reconstructions, count the number of cells reconstructed.
    d. For multimodals, count the number of cells processed.

