import os

from data_loaders import ProteinsDataLoader, miRNADataLoader, mRNADataLoader, PhenotypeDataLoader, SubtypesDataLoader, \
    DataLoader
from pipelines import (PhenotypePipeline, MultiDataframesPipeline, miRNAPipeline, mRNAPipeline,
                       ProteinsPipeline, SubTypesPipeline, DownstreamPipeline, Pipeline)
from src.analysis import get_metrics, get_metrics_comparison_plot, get_metrics_comparison_by_score_plot
from src.models import Data
from src.offline_analysis import run_all
from src.pipeline_steps import SimilarityMatrices, EncodeCategoricalData, KMedoids, ComputeKMedoids, \
    ComputeMatricesAverage, ComputeSNF, ComputeSpectralClustering
from loguru import logger
from sys import stdout

PROTEINS_PATH = '../data/mo_PRAD_RPPAArray-20160128.csv'
MIRNA_PATH = '../data/mo_PRAD_miRNASeqGene-20160128.csv'
MRNA_PATH = '../data/mo_PRAD_RNASeq2Gene-20160128.csv'
PHENOTYPE_PATH = '../data/mo_colData.csv'
SUBTYPES_PATH = '../data/subtypes.csv'

logger.remove()
logger.add(stdout, level='DEBUG', colorize=True,
           format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {extra[data_type]} | <level>{message}</level>')
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

proteins_data, mirna_data, mrna_data, phenotype_data, subtypes_data = MultiDataframesPipeline()(
    data=[proteins_data, mirna_data, mrna_data, phenotype_data, subtypes_data])
sim_proteins, sim_mirna, sim_mrna = SimilarityMatrices()(data=[proteins_data, mirna_data, mrna_data])

proteins_pred = ComputeKMedoids()(data=sim_proteins)
mirna_pred = ComputeKMedoids()(data=sim_mirna)
mrna_pred = ComputeKMedoids()(data=sim_mrna)

downstream_pipeline = DownstreamPipeline()
downstream_pipeline.steps = [ComputeMatricesAverage(), ComputeKMedoids()]
avg_pred = downstream_pipeline(data=[sim_proteins, sim_mirna, sim_mrna])

downstream_pipeline.steps = [ComputeSNF(), ComputeKMedoids()]
snf_pred = downstream_pipeline(data=[sim_proteins, sim_mirna, sim_mrna])

downstream_pipeline.steps = [ComputeSNF(), ComputeSpectralClustering()]
spectral_pred = downstream_pipeline(data=[sim_proteins, sim_mirna, sim_mrna])

encoded_subtypes = EncodeCategoricalData()(data=subtypes_data)['Subtype_Integrative']

proteins_metrics = get_metrics(true_labels=encoded_subtypes, predicted_labels=proteins_pred,
                               metrics_label='Proteins prediction metrics')
mirna_metrics = get_metrics(true_labels=encoded_subtypes, predicted_labels=mirna_pred,
                            metrics_label='miRNA prediction metrics')
mrna_metrics = get_metrics(true_labels=encoded_subtypes, predicted_labels=mrna_pred,
                           metrics_label='mRNA prediction metrics')
avg_metrics = get_metrics(true_labels=encoded_subtypes, predicted_labels=avg_pred,
                          metrics_label='Average prediction metrics')
snf_metrics = get_metrics(true_labels=encoded_subtypes, predicted_labels=snf_pred,
                          metrics_label='SNF prediction metrics')
spectral_pred = get_metrics(true_labels=encoded_subtypes, predicted_labels=spectral_pred,
                            metrics_label='Spectral prediction metrics')

proteins_metrics.plot().write_image('../plots/proteins_metrics.png')
mirna_metrics.plot().write_image('../plots/mirna_metrics.png')
mrna_metrics.plot().write_image('../plots/mrna_metrics.png')
avg_metrics.plot().write_image('../plots/avg_metrics.png')
snf_metrics.plot().write_image('../plots/snf_metrics.png')
spectral_pred.plot().write_image('../plots/spectral_pred.png')


get_metrics_comparison_plot([proteins_metrics, mirna_metrics, mrna_metrics, avg_metrics, snf_metrics, spectral_pred]).write_image('../plots/metrics_comparison.png')
get_metrics_comparison_by_score_plot([proteins_metrics, mirna_metrics, mrna_metrics, avg_metrics, snf_metrics, spectral_pred]).write_image('../plots/metrics_comparison_by_score.png')

run_all(plots_path=os.path.join('..', 'plots'))
