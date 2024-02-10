from pipelines import (PhenotypePipeline, MultiDataframesPipeline, miRNAPipeline, mRNAPipeline,
                       ProteinsPipeline, SubTypesPipeline, DownstreamPipeline, Pipeline)
from analysis import get_metrics, get_metrics_comparison_plot, get_metrics_comparison_by_score_plot, \
    plot_subtypes_distribution, plot_similarity_heatmap
from pipeline_steps import SimilarityMatrices, EncodeCategoricalData, ComputeKMedoids, \
    ComputeMatricesAverage, ComputeSNF, ComputeSpectralClustering
from data_loaders import ProteinsDataLoader, miRNADataLoader, mRNADataLoader, PhenotypeDataLoader, SubtypesDataLoader, \
    DataLoader
from plotly.graph_objs import Figure
from offline_analysis import run_all
from slugify import slugify
from loguru import logger
from models import Data
from sys import stdout

# Set the paths to the datasets
PROTEINS_PATH = '../data/mo_PRAD_RPPAArray-20160128.csv'
MIRNA_PATH = '../data/mo_PRAD_miRNASeqGene-20160128.csv'
MRNA_PATH = '../data/mo_PRAD_RNASeq2Gene-20160128.csv'
PHENOTYPE_PATH = '../data/mo_colData.csv'
SUBTYPES_PATH = '../data/subtypes.csv'

# Set up the logger
logger.remove()
logger.add(stdout, level='DEBUG', colorize=True,
           format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {extra[data_type]} | <level>{message}</level>')
logger.configure(extra={'data_type': 'None'})


def get_data(dataset_path: str, loader: DataLoader, pipeline: Pipeline) -> Data:
    """
    This method filters out the barcodes that correspond to primary tumors.

    Parameters
    ----------
    barcodes : list[str]
        The list of barcodes to be filtered. Each barcode is expected to have the tumor sample code at the 14th and 15th positions (0-indexed).

    Returns
    -------
    list[str]
        The list of barcodes that correspond to primary tumors.

    The method works as follows:
    1. It iterates over the given barcodes.
    2. For each barcode, it checks if it corresponds to a primary tumor using the is_primary_tumor method.
    3. It retains the barcodes that correspond to primary tumors in a list.
    4. It returns the list of barcodes that correspond to primary tumors.
    """

    data = loader.load(file_path=dataset_path)
    data = pipeline(data=data)
    return data


def save_plot(plot: Figure, extensionless_path: str):
    """
    This function saves the given plot as a PNG image and an HTML file.

    Parameters
    ----------
    plot : Figure
        The plot to be saved. This should be a plotly.graph_objs.Figure object.

    extensionless_path : str
        The path where the plot should be saved, without the file extension. The function will add the '.png' and '.html' extensions to this path when saving the plot.

    The function works as follows:
    1. It saves the plot as a PNG image at the given path with the '.png' extension.
    2. It saves the plot as an HTML file at the same path with the '.html' extension.
    """

    plot.write_image(f'{extensionless_path}.png')
    plot.write_html(f'{extensionless_path}.html')


# Load the datasets
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

# Prepare datasets for integration
proteins_data, mirna_data, mrna_data, phenotype_data, subtypes_data = MultiDataframesPipeline()(
    data=[proteins_data, mirna_data, mrna_data, phenotype_data, subtypes_data])

# Compute similarity matrices
sim_proteins, sim_mirna, sim_mrna = SimilarityMatrices()(data=[proteins_data, mirna_data, mrna_data])

# Cluster each similarity matrix separately
proteins_pred = ComputeKMedoids()(data=sim_proteins)
mirna_pred = ComputeKMedoids()(data=sim_mirna)
mrna_pred = ComputeKMedoids()(data=sim_mrna)

# Integrate the similarity matrices with average and cluster the integrated matrix
downstream_pipeline = DownstreamPipeline()
downstream_pipeline.steps = [ComputeMatricesAverage(), ComputeKMedoids()]
avg_pred = downstream_pipeline(data=[sim_proteins, sim_mirna, sim_mrna])

# Integrate the similarity matrices with SNF and cluster the integrated matrix
downstream_pipeline.steps = [ComputeSNF(), ComputeKMedoids()]
snf_pred = downstream_pipeline(data=[sim_proteins, sim_mirna, sim_mrna])

# Integrate the similarity matrices with SNF and cluster the integrated matrix using spectral clustering
downstream_pipeline.steps = [ComputeSNF(), ComputeSpectralClustering()]
spectral_pred = downstream_pipeline(data=[sim_proteins, sim_mirna, sim_mrna])

# Calculate metrics
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

# Save each metric's plot as a PNG image and an HTML file
save_plot(proteins_metrics.plot(), '../plots/proteins_metrics')
save_plot(mirna_metrics.plot(), '../plots/mirna_metrics')
save_plot(mrna_metrics.plot(), '../plots/mrna_metrics')
save_plot(avg_metrics.plot(), '../plots/avg_metrics')
save_plot(snf_metrics.plot(), '../plots/snf_metrics')
save_plot(spectral_metrics.plot(), '../plots/spectral_metrics')

# Save the comparison of the metrics as a PNG image and an HTML file
save_plot(get_metrics_comparison_plot(
    [proteins_metrics, mirna_metrics, mrna_metrics, avg_metrics, snf_metrics, spectral_metrics]),
    '../plots/metrics_comparison')

# Save the comparison of the metrics grouped by score as a PNG image and an HTML file
save_plot(get_metrics_comparison_by_score_plot(
    [proteins_metrics, mirna_metrics, mrna_metrics, avg_metrics, snf_metrics, spectral_metrics]),
    '../plots/metrics_comparison_by_score')

# Save the subtypes distribution plot as a PNG image and an HTML file
save_plot(plot_subtypes_distribution(subtypes_data), '../plots/subtypes_distribution')

# Save the similarity matrices as PNG images and HTML files
save_plot(plot_similarity_heatmap(sim_proteins, data_type='Proteins'), '../plots/proteins_similarity_heatmap')
save_plot(plot_similarity_heatmap(sim_mirna, data_type='miRNA'), '../plots/mirna_similarity_heatmap')
save_plot(plot_similarity_heatmap(sim_mrna, data_type='mRNA'), '../plots/mrna_similarity_heatmap')

# Run all offline analysis
offline_plots = run_all()

# Save the plots from the offline analysis as PNG images and HTML files
for plot in offline_plots:
    save_plot(plot, f'../plots/{slugify(plot.layout.title.text)}')
