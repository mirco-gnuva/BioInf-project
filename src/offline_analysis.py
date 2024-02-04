import numpy as np
from tqdm import tqdm

from data_loaders import (ProteinsDataLoader, miRNADataLoader, mRNADataLoader, PhenotypeDataLoader, SubtypesDataLoader,
                          DataLoader)
import plotly.express as px
from loguru import logger
from sys import stdout

from src.models import Data
from src.pipeline_steps import RetainMainTumors
from src.pipelines import ProteinsPipeline, Pipeline, miRNAPipeline, PhenotypePipeline, SubTypesPipeline
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import os
from scipy.stats import shapiro

PROTEINS_PATH = '../data/mo_PRAD_RPPAArray-20160128.csv'
MIRNA_PATH = '../data/mo_PRAD_miRNASeqGene-20160128.csv'
MRNA_PATH = '../data/mo_PRAD_RNASeq2Gene-20160128.csv'
PHENOTYPE_PATH = '../data/mo_colData.csv'
SUBTYPES_PATH = '../data/subtypes.csv'

logger.remove()
logger.add(stdout, level='DEBUG', colorize=True,
           format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {extra[data_type]} | <level>{message}</level>')
logger.configure(extra={'data_type': 'None'})

proteins_pipeline = ProteinsPipeline()
proteins_pipeline.steps = [RetainMainTumors()]
proteins_loader = ProteinsDataLoader()
proteins_data = proteins_loader.load(file_path=PROTEINS_PATH)

mirna_pipeline = miRNAPipeline()
mirna_pipeline.steps = [RetainMainTumors()]
mirna_loader = miRNADataLoader()
mirna_data = mirna_loader.load(file_path=MIRNA_PATH)

mrna_pipeline = miRNAPipeline()
mrna_pipeline.steps = [RetainMainTumors()]
mrna_loader = mRNADataLoader()
mrna_data = mrna_loader.load(file_path=MRNA_PATH)

phenotype_pipeline = PhenotypePipeline()
phenotype_loader = PhenotypeDataLoader()
phenotype_data = phenotype_loader.load(file_path=PHENOTYPE_PATH)


# subtypes_pipeline = SubTypesPipeline()
# subtypes_loader = SubtypesDataLoader()
# subtypes_data = subtypes_loader.load(file_path=SUBTYPES_PATH)


def plot_features_with_nans(dump_path: str, show: bool = False):
    proteins_features = len(proteins_data.columns)
    proteins_features_with_nans = sum(proteins_data.isna().sum() > 0)
    proteins_nans_percentage = proteins_features_with_nans / proteins_features * 100

    mirna_features = len(mirna_data.columns)
    mirna_features_with_nans = sum(mirna_data.isna().sum() > 0)
    mirna_features_with_nans_percentage = mirna_features_with_nans / mirna_features * 100

    mrna_features = len(mrna_data.columns)
    mrna_features_with_nans = sum(mrna_data.isna().sum() > 0)
    mrna_features_with_nans_percentage = mrna_features_with_nans / mrna_features * 100

    data = pd.DataFrame([['Proteins', proteins_features_with_nans, proteins_nans_percentage],
                         ['miRNA', mirna_features_with_nans, mirna_features_with_nans_percentage],
                         ['mRNA', mrna_features_with_nans, mrna_features_with_nans_percentage]],
                        columns=['Data Type', 'NaNs features count', 'Percentage'])

    fig = px.bar(data, x='Data Type', y='Percentage', hover_data=['NaNs features count'], )

    fig.update_layout(title='Total Features vs Features with NaNs',
                      title_x=0.5,
                      xaxis_title='Data Type',
                      yaxis_title='% of features with NaNs',
                      yaxis_range=[0, 100])

    if show:
        fig.show()

    fig.write_image(dump_path)


def plot_nan_percetage_per_feature(data: pd.DataFrame, data_type: str, dump_path: str, show: bool = False):
    data = data.isna().sum() / len(data) * 100
    data = data.to_frame()
    data.columns = ['NaNs Percentage']
    data = data[data['NaNs Percentage'] > 0]
    data['Feature'] = data.index
    data['Data Type'] = data_type

    fig = px.bar(data, x='Feature', y='NaNs Percentage',
                 color='Feature',
                 hover_data=['NaNs Percentage'],
                 color_discrete_sequence=px.colors.qualitative.Safe)

    fig.update_layout(title='NaNs Percentage per Feature',
                      title_x=0.5,
                      xaxis_title='Feature',
                      yaxis_title='% of NaNs',
                      yaxis_range=[0, 100])

    if show:
        fig.show()

    fig.write_image(dump_path)


def plot_features_pearson_correlation(data: pd.DataFrame, data_type: str, dump_path: str, show: bool = False):
    # corr = data.corr()
    corr = np.corrcoef(data, rowvar=False)
    triu_indices = np.triu_indices(corr.shape[0], 1)

    feature_pairs = ((data.columns[i], data.columns[j]) for i, j in zip(*triu_indices))

    correlations = corr[triu_indices]
    result = np.array([(pair[0], pair[1], corr) for pair, corr in zip(feature_pairs, correlations)])

    # raw_data = []
    # for i in tqdm(range(len(corr)), leave=False):
    #     for j in tqdm(range(len(corr)), leave=False):
    #         raw_data.append({'Feature 1': corr.index[i],
    #                          'Feature 2': corr.columns[j],
    #                          'Correlation': corr.iloc[i, j]})
    #
    # df = pd.DataFrame(raw_data, columns=['Feature 1', 'Feature 2', 'Correlation'])

    # df = pd.DataFrame(({'Feature 1': corr.index[i],
    #                     'Feature 2': corr.columns[j],
    #                     'Correlation': corr.iloc[i, j]} for i in range(len(corr)) for j in range(len(corr))),
    #                   columns=['Feature 1', 'Feature 2', 'Correlation'])
    df = corr.stack()
    df.index.names = ['Feature 1', 'Feature 2']
    df = df.reset_index(level=['Feature 2']).reset_index()
    df.columns = ['Feature 1', 'Feature 2', 'Correlation']

    fig = px.density_heatmap(df, x='Feature 1', y='Feature 2', z='Correlation')

    fig.update_layout(title=f'Features Pearson correlation ({data_type})',
                      title_x=0.5,
                      xaxis_title='Feature',
                      yaxis_title='Feature')

    if show:
        fig.show()

    fig.write_image(dump_path)


def run_all(plots_path: str = '../plots', show: bool = False):
    plot_features_with_nans(dump_path=os.path.join(plots_path, 'nans_perc_plot.png'), show=show)
    plot_nan_percetage_per_feature(data=proteins_data, data_type='Proteins',
                                   dump_path=os.path.join(plots_path, 'proteins_nans_perc.png'), show=show)
    plot_nan_percetage_per_feature(data=mirna_data, data_type='miRNA',
                                   dump_path=os.path.join(plots_path, 'mirna_nans_perc.png'), show=show)
    plot_nan_percetage_per_feature(data=mrna_data, data_type='mRNA',
                                   dump_path=os.path.join(plots_path, 'mrna_nans_perc.png'), show=show)
    # plot_features_pearson_correlation(data=proteins_data, data_type='Proteins',
    #                                   dump_path=os.path.join(plots_path, 'proteins_corr.png'), show=show)
    # plot_features_pearson_correlation(data=mirna_data, data_type='miRNA',
    #                                   dump_path=os.path.join(plots_path, 'mirna_corr.png'), show=show)
    plot_features_pearson_correlation(data=mrna_data, data_type='mRNA',
                                      dump_path=os.path.join(plots_path, 'mrna_corr.png'), show=show)
