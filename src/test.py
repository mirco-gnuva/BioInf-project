from data_handling import ProteinsDataLoader, miRNADataLoader, mRNADataLoader, ClinicalDataLoader
from pipelines import DownstreamPipeline
from analysis import get_nan_percentage

proteins_loader = ProteinsDataLoader()

proteins_data = proteins_loader.load(file_path='../data/mo_PRAD_RPPAArray-20160128.csv')

mirna_loader = miRNADataLoader()

mirna_data = mirna_loader.load(file_path='../data/mo_PRAD_miRNASeqGene-20160128.csv')

mrna_loader = mRNADataLoader()

mrna_data = mrna_loader.load(file_path='../data/mo_PRAD_RNASeq2Gene-20160128.csv')

clinical_loader = ClinicalDataLoader()

clinical_data = clinical_loader.load(file_path='../data/mo_colData.csv')

downstream_pipeline = DownstreamPipeline()

result = downstream_pipeline(data=[proteins_data, mirna_data, mrna_data, clinical_data])

nan_percs = get_nan_percentage(data=result)

nan_percs.sort(key=lambda x: x.percentage, reverse=True)

pass
