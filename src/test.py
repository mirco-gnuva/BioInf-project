from data_handling import ProteinsDataLoader, miRNADataLoader

proteins_loader = ProteinsDataLoader(file_path='/Users/mirco.gnuva/Documents/BioInf-project/src/data/mo_PRAD_RPPAArray-20160128.csv')

proteins_data = proteins_loader.load()

mirna_loader = miRNADataLoader(file_path='/Users/mirco.gnuva/Documents/BioInf-project/src/data/mo_PRAD_miRNASeqGene-20160128.csv')

mirna_data = mirna_loader.load()


pass
