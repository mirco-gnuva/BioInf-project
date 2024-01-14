import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

# Activate the R package manager (BiocManager)
utils = importr('utils')

# Install BiocManager if not already installed

utils.install_packages('BiocManager')

# Load BiocManager
BiocManager = importr('BiocManager')

# Install curatedTCGAData
BiocManager.install("curatedTCGAData")
