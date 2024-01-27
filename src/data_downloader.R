# Select the first mirror for packages download
chooseCRANmirror(ind=1)


# Define requirements
requirements <- c("bslib", "BiocManager", "SNFtool", "NetPreProc", "caret", "cluster", "mclustcomp")
bioc_requirements <- c("curatedTCGAData", "TCGAutils", "TCGAbiolinks", "graph")


# Install the requirements
for (req in requirements){
  if (!require(req, quietly = TRUE))
    install.packages(req);
}

for (req in bioc_requirements){
  if (!require(req, quietly = TRUE))
    BiocManager::install(req);
}


# Import libraries
library("curatedTCGAData")
library(TCGAbiolinks)

# Define download directory
directory_path = './data/'

if (file.exists(directory_path)) {
  print(paste("Directory", directory_path, "already exists."))
} else {
  print(paste("Creating", directory_path))
  dir.create(directory_path, showWarnings = FALSE)
  
  # Check if the directory was created successfully
  if (file.exists(directory_path)) {
    print(paste("Directory", directory_path, "created successfully."))
  } else {
    print(paste("Failed to create directory", directory_path))
  }
}


# Download the TCGA data
assays <- c("miRNASeqGene", "RNASeq2Gene", "RPPAArray");
mo <- curatedTCGAData(diseaseCode = "PRAD", 
                      assays = assays, 
                      version = "2.0.1", dry.run = FALSE);

mo;


# Export the downloaded data to directory_path folder
exportClass(mo, dir = directory_path, fmt = "csv", ext = ".csv");


# Download disease subtypes from TCGAbiolinks:
subtypes <- as.data.frame(TCGAbiolinks::PanCancerAtlas_subtypes());
subtypes <- subtypes[subtypes$cancer.type == "PRAD", ];
subtypes_path <- paste(directory_path, "subtypes.csv", sep="")

print(paste("Saving subtypes to", subtypes_path))

write.csv(subtypes, file = subtypes_path, row.names = FALSE)
