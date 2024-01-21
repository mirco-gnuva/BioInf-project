import os

os.environ["R_HOME"] = r"C:\Program Files\R\R-4.3.2"
os.environ["PATH"] = r"C:\Program Files\R\R-4.3.2\bin\x64" + ";" + os.environ["PATH"]

import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

r_requiremnts = ['BiocManager', 'SNFtool', 'NetPreProc', 'caret', 'cluster', 'mclustcomp']
biocmanager_requirements = ['curatedTCGAData', 'TCGAutils', 'TCGAbiolinks']

# Activate the R package manager (BiocManager)
utils = importr('utils')

# Install BiocManager if not already installed

for req in r_requiremnts:
    utils.install_packages(req)

BiocManager = importr('BiocManager')

for req in biocmanager_requirements:
    BiocManager.install(req)

curatedTCGAData = importr("curatedTCGAData")
importr("TCGAbiolinks")
importr("TCGAutils")
importr("SNFtool")
importr("NetPreProc")
importr("caret")
importr("cluster")
importr("mclustcomp")

assays = ["miRNASeqGene", "RNASeq2Gene", "RPPAArray"]
mo = curatedTCGAData(diseaseCode="PRAD",
                     assays=assays,
                     version="2.0.1", dry_run=False)
