from data_loaders import ProteinsDataLoader, miRNADataLoader, mRNADataLoader, PhenotypeDataLoader, SubtypesDataLoader, \
    DataLoader
from pipelines import (PhenotypePipeline, MultiDataframesPipeline, miRNAPipeline, mRNAPipeline,
                       ProteinsPipeline, SubTypesPipeline, DownstreamPipeline, Pipeline)
from src.analysis import get_metrics
from src.models import Data
from src.pipeline_steps import SimilarityMatrices, EncodeCategoricalData
from loguru import logger
from sys import stdout

PROTEINS_PATH = '../data/mo_PRAD_RPPAArray-20160128.csv'
MIRNA_PATH = '../data/mo_PRAD_miRNASeqGene-20160128.csv'
MRNA_PATH = '../data/mo_PRAD_RNASeq2Gene-20160128.csv'
PHENOTYPE_PATH = '../data/mo_colData.csv'
SUBTYPES_PATH = '../data/subtypes.csv'

logger.remove()
logger.add(stdout, level='DEBUG', colorize=True, format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {extra[data_type]} | <level>{message}</level>')
logger.configure(extra={'data_type': 'None'})


def get_data(dataset_path: str, loader: DataLoader, pipeline: Pipeline) -> Data:
    data = loader.load(file_path=dataset_path)
    data = pipeline(data=data)
    return data


proteins_data = get_data(dataset_path=PROTEINS_PATH,
                         loader=ProteinsDataLoader(),
                         pipeline=ProteinsPipeline())

mirna_data = get_data(dataset_path=MIRNA_PATH,
                      loader=miRNADataLoader(),
                      pipeline=miRNAPipeline())

mrna_data = get_data(dataset_path=MRNA_PATH,
                     loader=mRNADataLoader(),
                     pipeline=mRNAPipeline())

phenotype_data = get_data(dataset_path=PHENOTYPE_PATH,
                          loader=PhenotypeDataLoader(),
                          pipeline=PhenotypePipeline())

subtypes_data = get_data(dataset_path=SUBTYPES_PATH,
                         loader=SubtypesDataLoader(),
                         pipeline=SubTypesPipeline())


proteins_data, mirna_data, mrna_data, phenotype_data, subtypes_data = MultiDataframesPipeline()(data=[proteins_data, mirna_data, mrna_data, phenotype_data, subtypes_data])
sim_proteins, sim_mirna, sim_mrna = SimilarityMatrices()(data=[proteins_data, mirna_data, mrna_data])


downstream_pipeline = DownstreamPipeline()


pred_clusters = downstream_pipeline(data=[sim_proteins, sim_mirna, sim_mrna]).labels_

encoded_subtypes = EncodeCategoricalData()(data=subtypes_data)['Subtype_Integrative']

metrics = get_metrics(true_labels=encoded_subtypes, predicted_labels=pred_clusters)

metrics.plot().show()
