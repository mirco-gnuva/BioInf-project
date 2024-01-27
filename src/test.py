from data_handling import ProteinsDataLoader, miRNADataLoader, mRNADataLoader, PhenotypeDataLoader
from pipelines import (PhenotypePipeline, MultiDataframesPipeline, miRNAPipeline, mRNAPipeline,
                       ProteinsPipeline)

proteins_loader = ProteinsDataLoader()

proteins_data = proteins_loader.load(file_path='../data/mo_PRAD_RPPAArray-20160128.csv')

mirna_loader = miRNADataLoader()

mirna_data = mirna_loader.load(file_path='../data/mo_PRAD_miRNASeqGene-20160128.csv')

mrna_loader = mRNADataLoader()

mrna_data = mrna_loader.load(file_path='../data/mo_PRAD_RNASeq2Gene-20160128.csv')

phenotype_loader = PhenotypeDataLoader()

phenotype_data = phenotype_loader.load(file_path='../data/mo_colData.csv')

phenotype_pipeline = PhenotypePipeline()
phenotype_data = phenotype_pipeline(data=phenotype_data)

proteins_data = ProteinsPipeline()(data=proteins_data)
mirna_data = miRNAPipeline()(data=mirna_data)
mrna_data = mRNAPipeline()(data=mrna_data)

multi_dataframes_pipeline = MultiDataframesPipeline()

proteins_data, mirna_data, mrna_data, phenotype_data = multi_dataframes_pipeline(
    data=[proteins_data, mirna_data, mrna_data, phenotype_data])

pass
