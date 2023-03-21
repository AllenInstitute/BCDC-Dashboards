### count categories
## data_type count (for sample type, column B)
data_type_map = {
    'brain_types' : ['brain hemisphere', 
                     'brain region', 
                     'brain section set', 
                     'brain slice', 
                     'whole brain', 
                     'spinal cord'],
    'cell_types' : ['cell body', 
                    'cell in slice', 
                    'bulk nucleus', 
                    'cell nucleus', 
                    'cell suspension', 
                    'reconstruction', 
                    'whole cell']
        

}

## specimen count (for specimens, column N)
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


### collapse categories
## for species, column D
species_map = {
    'primates' : ['chimpanzee', 'small-eared galago', 'western gorilla', 'green monkey', 'pig-tailed macaque',
                 "ma's night monkey", 'rhesus macaque', 'bolivian squirrel monkey',
       'crab-eating macaque'],
    'humans' : ['human'], ## mostly mice and humans
    'mice' : ['mouse'],
    'marmoset': ['marmoset'],
    'small mammals': [
    'arctic ground squirrel',
    'nine-banded armadillo',
    'domestic cat',
    'domestic ferret',
    'gray short-tailed opossum',
    'pig', 'rabbit', 'norway rat', 'common tree shrew'
    ]
}

## for techniques, column L
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




