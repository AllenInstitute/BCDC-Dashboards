# BCDC-Dashboards
This repository is intended to store the codes for the BICAN dashboard, which takes the BCDC-Metadata repository as the input, performs data wrangling and launches the dashboard app script. The current version is a demo version that lives in the local environment and has not been integrated with the other pipelines yet, hence, the code structures are subject to change once the integration with the rest of the existing pipelines (i.e. databases, ontologies) happens.

### Workflow
1. Input: BCDC-Metadata
2. Data Wrangling: dashboard_data_wrangling.ipynb
    Output: dash_count_df.csv
3. Dashboard script: tast_dash_counts.py (takes dash_count_df.csv as input)
    Output: Dashboard page with visualizations

### Business logics:

[dashboard_logic_components.pdf](https://github.com/AllenInstitute/BCDC-Dashboards/files/11044153/dashboard_logic_components.pdf)


Currently, we are aiming to count the below units:
1. Number of samples received for each sample type per group - for example, how many brain/cell related samples did we receive per quarter; or for each grant?
2. Number of donors/subjects per group - for example, how many donors/subjects per quarter/modality/technique?
3. Number of subspecimens (brains, cells, tissue samples, etc.) processed per quarter/grant/technique/etc.

While counting, the groups and categories will be collapsed into similar terminologies to reduce the complexity of the plots so that they are more readable, and the grouping will be done primarily for sample types, specimen types, species, techniques, and modalities. It is expected that this pipeline will be connected with external taxonomy/ontology hierarchies to determine the most interoperable way of collapsing the terminologies.
