import os

from plotly.graph_objs import Figure

from data_loaders import ProteinsDataLoader, miRNADataLoader, mRNADataLoader, PhenotypeDataLoader, SubtypesDataLoader, \
    DataLoader
from pipelines import (PhenotypePipeline, MultiDataframesPipeline, miRNAPipeline, mRNAPipeline,
                       ProteinsPipeline, SubTypesPipeline, DownstreamPipeline, Pipeline)
from analysis import get_metrics, get_metrics_comparison_plot, get_metrics_comparison_by_score_plot, \
    get_silhouette_score_plot, plot_subtypes_distribution, plot_similarity_heatmap
from models import Data
from offline_analysis import run_all
from pipeline_steps import SimilarityMatrices, EncodeCategoricalData, ComputeKMedoids, \
    ComputeMatricesAverage, ComputeSNF, ComputeSpectralClustering
from loguru import logger
from sys import stdout
from slugify import slugify

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


def save_plot(plot: Figure, extensionless_path: str):
    plot.write_image(f'{extensionless_path}.png')
    plot.write_html(f'{extensionless_path}.html')


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
                               metrics_label='Proteins prediction metrics', similarity_data=sim_proteins)
mirna_metrics = get_metrics(true_labels=encoded_subtypes, predicted_labels=mirna_pred,
                            metrics_label='miRNA prediction metrics', similarity_data=sim_mirna)
mrna_metrics = get_metrics(true_labels=encoded_subtypes, predicted_labels=mrna_pred,
                           metrics_label='mRNA prediction metrics', similarity_data=sim_mrna)
avg_metrics = get_metrics(true_labels=encoded_subtypes, predicted_labels=avg_pred,
                          metrics_label='Average prediction metrics',
                          similarity_data=ComputeMatricesAverage()(data=[sim_proteins, sim_mirna, sim_mrna]))
snf_metrics = get_metrics(true_labels=encoded_subtypes, predicted_labels=snf_pred,
                          metrics_label='SNF prediction metrics',
                          similarity_data=ComputeSNF()(data=[sim_proteins, sim_mirna, sim_mrna]))
spectral_metrics = get_metrics(true_labels=encoded_subtypes, predicted_labels=spectral_pred,
                               metrics_label='Spectral prediction metrics',
                               similarity_data=ComputeSNF()(data=[sim_proteins, sim_mirna, sim_mrna]))

save_plot(proteins_metrics.plot(), '../plots/proteins_metrics')
save_plot(mirna_metrics.plot(), '../plots/mirna_metrics')
save_plot(mrna_metrics.plot(), '../plots/mrna_metrics')
save_plot(avg_metrics.plot(), '../plots/avg_metrics')
save_plot(snf_metrics.plot(), '../plots/snf_metrics')
save_plot(spectral_metrics.plot(), '../plots/spectral_metrics')

save_plot(get_metrics_comparison_plot(
    [proteins_metrics, mirna_metrics, mrna_metrics, avg_metrics, snf_metrics, spectral_metrics]),
    '../plots/metrics_comparison')

save_plot(get_metrics_comparison_by_score_plot(
    [proteins_metrics, mirna_metrics, mrna_metrics, avg_metrics, snf_metrics, spectral_metrics]),
    '../plots/metrics_comparison_by_score')

save_plot(get_silhouette_score_plot(predicted_labels=spectral_pred,
                                    similarity_data=ComputeSNF()(data=[sim_proteins, sim_mirna, sim_mrna])),
          '../plots/silhouette_score')

save_plot(plot_subtypes_distribution(subtypes_data), '../plots/subtypes_distribution')

save_plot(plot_similarity_heatmap(sim_proteins, data_type='Proteins'), '../plots/proteins_similarity_heatmap')
save_plot(plot_similarity_heatmap(sim_mirna, data_type='miRNA'), '../plots/mirna_similarity_heatmap')
save_plot(plot_similarity_heatmap(sim_mrna, data_type='mRNA'), '../plots/mrna_similarity_heatmap')

offline_plots = run_all()

for plot in offline_plots:
    save_plot(plot, f'../plots/{slugify(plot.layout.title.text)}')


