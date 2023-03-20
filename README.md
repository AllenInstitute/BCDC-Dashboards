# BCDC-Dashboards
This repository is intended to store the codes for the BICAN dashboard, which takes the BCDC-Metadata repository as the input, performs data wrangling and launches the dashboard app script. The current version is a demo version that lives in the local environment and has not been integrated with the other pipelines yet, hence, the code structures are subject to change once the integration with the rest of the existing pipelines (i.e. databases, ontologies) happens.

Disclaimer: the current dashboard script has not included any 'techniques'-related count functionalities, however, an abstract of categories to collapse into has been included in the business logics.


### Workflow
1. Input: BCDC-Metadata
2. Data Wrangling: dashboard_data_wrangling.ipynb
    Output: dash_count_df.csv
3. Dashboard script: tast_dash_counts.py (takes dash_count_df.csv as input)
    Output: Dashboard page with visualizations

### Business logics:
Currently, we are aiming to count the below units:
1. Number of samples received for each sample type per group - for example, how many brain/cell related samples did we receive per quarter; or for each grant?
2. Number of donors/subjects per group - for example, how many donors/subjects per quarter/modality/technique?
3. Number of subspecimens (brains, cells, tissue samples, etc.) processed per quarter/grant/technique/etc.

While counting, the groups and categories will be collapsed into similar terminologies - for example, 'whole cell' and 'cell body' both mean the same thing, and as a result, they will be collapsed together under 'cells' and their counts will be counted towards the same category.

Specific logics for subspecimen counts is represented in the below dictionary:

```
specimen_count_map = {
    'brains' : ['whole brain',
                'brain', 'brains'], # fix the plural
    'cells' : ['whole cell', 
               'cell', 'cells', 'cell body', 'cell suspension', 'cell nucleus', 'nuclei', 'resconstruction', 'cell in slice'],
    'nucleus' : ['cell nucleus', 
                 'nuclei'],
    'library' : ['library'],
    'tissue samples' : ['brain hemisphere', 
                        'brain region', 
                        'brain section set', 
                        'brain slice', 
                        'library', 
                        'spinal cord slice',
                        'tissue sample']   
}
```

Similar logics apply for techniques as well - for example, 10x Chromium 3' v2, v3 and v3.1 sequencing techniques should be collapsed into the same category.

```
techniques_map = {
    'multimodal': [
    'Patch-seq',
    'SHARE-seq',
    '10X Genomics Multiome'
    ], 
    'epigenomics': [
    'ATAC-seq',
    'snmC-seq2',
    'snm3C-seq',
    ], 
    '10x Chromium techniques': [
    "10x Chromium 3' v2 sequencing",
    "10x Chromium 3' v3.1 sequencing",
    "10x Chromium 3' v3 sequencing"
    ],
    "imaging" : [
    'MRI', 
    'OCT',
    "STPT",
    "lightsheet microscopy",
    "mouselight", 
    "confrocal microscopy",
    "VISor"

    ],
    "spatial" :[
    'FISH',
    'SeqFISH',
    'MERFISH',
    'Slide-seq'
    ]
}
```

The usage of such dictionary is represented in the data wrangling script dashboard_data_wrangling.ipynb; some other columns, such as techniques, will also be collapsed in a similar manner. Please refer to the category_maps.py file for detailed views.

