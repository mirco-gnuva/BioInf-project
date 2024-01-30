from data_loaders import (ProteinsDataLoader, miRNADataLoader, mRNADataLoader, PhenotypeDataLoader, SubtypesDataLoader,
                          DataLoader)
import plotly.express as px
from loguru import logger
from sys import stdout

from src.models import Data
from src.pipeline_steps import RetainMainTumors
from src.pipelines import ProteinsPipeline, Pipeline, miRNAPipeline, PhenotypePipeline, SubTypesPipeline
import pandas as pd
import os

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
                      yaxis_title='% of features with NaNs')

    if show:
        fig.show()

    fig.write_image(dump_path)


def plt_nan_percetage_per_feature(data: pd.DataFrame, data_type: str, dump_path: str, show: bool = False):
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
                      yaxis_title='% of NaNs')

    if show:
        fig.show()

    fig.write_image(dump_path)


plot_features_with_nans(dump_path='../plots/plot.png')
plt_nan_percetage_per_feature(data=proteins_data, data_type='Proteins', dump_path='../plots/proteins.png')
