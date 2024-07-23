# EasyAstro : a set of astronomy python-based notebooks for amateurs:
- easyviewer : generic FIT images viewer (USABLE - LEFT TO DO: more file formats to support)
- easyreduce : images preprocessing (USABLE - LEFT TO DO: image combiner to refactor, cosmicray removal, RTS noise removal)
- easyspectrum : long-slit spectrum extract, calibrate and analysis (USABLE - LEFT TO DO : code cleanup, ref. star selection))
- easyplan : display info, field-of-view, altitude of target (USABLE - LEFT TO DO: more infos to show)
- easyphot : reduce and analyse variable stars (or exoplanet) time series (NOT STARTED - DEMO ONLY)

# Installation:
- install miniforge3 : https://github.com/conda-forge/miniforge 
- create (or reuse your base env) a python environment : $ conda env update --file environment.yml
- install required packages :  $ pip install -r requirements.txt --upgrade
- start jupyter lab (or notebook) : $ jupyter lab
- open a notebook...
  
# References : 
- astropy workshop from https://github.com/astropy/astropy-workshop
- JWST data exploration : https://jwst-docs.stsci.edu/jwst-post-pipeline-data-analysis/data-analysis-example-jupyter-notebooks
- python cookbook from https://github.com/ipython-books/cookbook-2nd
- code snippets from https://prancer.physics.louisville.edu/classes/650/python/examples/
- astro-datalab from https://datalab.noirlab.edu
