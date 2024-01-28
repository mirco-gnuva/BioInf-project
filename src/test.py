from data_loaders import ProteinsDataLoader, miRNADataLoader, mRNADataLoader, PhenotypeDataLoader, SubtypesDataLoader
from pipelines import (PhenotypePipeline, MultiDataframesPipeline, miRNAPipeline, mRNAPipeline,
                       ProteinsPipeline, SubTypesPipeline, DownstreamPipeline)
from src.analysis import get_subtypes_distribution
from src.pipeline_steps import IntersectDataframes, SimilarityMatrices, EncodeCategoricalData
from sklearn.metrics.cluster import rand_score

proteins_loader = ProteinsDataLoader()
proteins_data = proteins_loader.load(file_path='../data/mo_PRAD_RPPAArray-20160128.csv')
proteins_data = ProteinsPipeline()(data=proteins_data)

mirna_loader = miRNADataLoader()
mirna_data = mirna_loader.load(file_path='../data/mo_PRAD_miRNASeqGene-20160128.csv')
mirna_data = miRNAPipeline()(data=mirna_data)

mrna_loader = mRNADataLoader()
mrna_data = mrna_loader.load(file_path='../data/mo_PRAD_RNASeq2Gene-20160128.csv')
mrna_data = mRNAPipeline()(data=mrna_data)

phenotype_loader = PhenotypeDataLoader()
phenotype_data = phenotype_loader.load(file_path='../data/mo_colData.csv')
phenotype_data = PhenotypePipeline()(data=phenotype_data)

subtypes_loader = SubtypesDataLoader()
subtypes_data = subtypes_loader.load(file_path='../data/subtypes.csv')
subtypes_data = SubTypesPipeline()(data=subtypes_data)


proteins_data, mirna_data, mrna_data, phenotype_data, subtypes_data = MultiDataframesPipeline()(data=[proteins_data, mirna_data, mrna_data, phenotype_data, subtypes_data])
sim_proteins, sim_mirna, sim_mrna = SimilarityMatrices()(data=[proteins_data, mirna_data, mrna_data])

downstream_pipeline = DownstreamPipeline()
kmeoids = downstream_pipeline(data=[sim_proteins, sim_mirna, sim_mrna])


encoded_subtypes = EncodeCategoricalData()(data=subtypes_data)['Subtype_Integrative']

pass
