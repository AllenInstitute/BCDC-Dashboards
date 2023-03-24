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
               'cell', 'cells', 'cell body', 'cell suspension', 'cell nucleus', 'nuclei', 'resconstruction', 'cell in slice'],,
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

## technology vs the modality they should belong to
modality_tech_map = {
    'multimodal': ['whole cell patch clamp', 'patch-seq', 'share-seq', '10x genomics multiome', '10x chromium multiome'], 
    'epigenomics': ['atac-seq', 'sci-atac-seq3', 'mC-seq2'], 
    'anatomy/morphology' : ['cre-dependent anterograde tracing', 'anterograde tracing', 'retrograde tracing', 
                            'neuron morphology reconstruction', 'retrograde transsynaptic tracing', 
                            'enhancer virus labeling', 'morf genetic sparse labeling', 'histology', 'trio tracing', 
                           'stereology', 'triple anterograde', 'olst'], # triple?
    "imaging" : ['confrocal microscopy', 'confocal microscopy', 'stpt', 'pct', 'oct', "lightsheet microscopy", "light sheet microscopy", "mouselight", 'mri', 'cisi', 'fmost',
                 'visor'], # typo here
    "spatial" : ['fish', 'seqfish', 'merfish', 'slide-seq', 'smfish'],
    'transcriptomics' : ['10x chromium 3\' sequencing', 'smart-seq v4', 'sci-rna-seq3', 'drop-seq', 'dnaseq', 'pacbio long read sequencing']
    
}