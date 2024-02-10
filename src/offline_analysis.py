from data_loaders import ProteinsDataLoader, miRNADataLoader, mRNADataLoader, PhenotypeDataLoader
from settings import PROTEINS_PATH, MIRNA_PATH, MRNA_PATH, PHENOTYPE_PATH, SUBTYPES_PATH
from pipelines import ProteinsPipeline, miRNAPipeline, PhenotypePipeline
from pipeline_steps import RetainMainTumors
from plotly.graph_objs import Figure
from typing import Generator
import plotly.express as px
from loguru import logger
from sys import stdout
import pandas as pd

# Set up the logger
logger.remove()
logger.add(stdout, level='DEBUG', colorize=True,
           format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {extra[data_type]} | <level>{message}</level>')
logger.configure(extra={'data_type': 'None'})

# Load the data
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


def plot_features_with_nans(show: bool = False) -> Figure:
    """
    This function creates a bar plot showing the percentage of features with NaN values in the Proteins, miRNA, and mRNA datasets.

    Parameters
    ----------
    show : bool, optional
        If True, the plot is displayed. If False, the plot is not displayed. The default is False.

    Returns
    -------
    Figure
        The created plotly.graph_objs.Figure object representing the bar plot.

    The function works as follows:
    1. It calculates the total number of features and the number of features with NaN values in each dataset.
    2. It calculates the percentage of features with NaN values in each dataset.
    3. It creates a DataFrame with the calculated data.
    4. It creates a bar plot from the DataFrame using plotly.
    5. It updates the layout and traces of the plot.
    6. If the show parameter is True, it displays the plot.
    7. It returns the created plot.
    """

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

    fig = px.bar(data, x='Data Type', y='Percentage', hover_data=['NaNs features count'], text='Percentage',
                 color_discrete_sequence=px.colors.qualitative.Safe)

    fig.update_layout(title='Total Features vs Features with NaNs',
                      title_x=0.5,
                      xaxis_title='Data Type',
                      yaxis_title='% of features with NaNs',
                      yaxis_range=[0, 100])

    fig.update_traces(textposition='outside', texttemplate='%{text:.2f}%')

    if show:
        fig.show()

    return fig


def plot_nan_percentage_per_feature(data: pd.DataFrame, data_type: str, show: bool = False):
    """
    This function creates a bar plot showing the percentage of NaN values per feature in the given dataset.

    Parameters
    ----------
    data : pd.DataFrame
        The dataset to be analyzed. This should be a pandas DataFrame where each column represents a feature and each row represents a sample.

    data_type : str
        The type of the data. This is used to label the data in the plot.

    show : bool, optional
        If True, the plot is displayed. If False, the plot is not displayed. The default is False.

    Returns
    -------
    Figure
        The created plotly.graph_objs.Figure object representing the bar plot.

    The function works as follows:
    1. It calculates the percentage of NaN values for each feature in the dataset.
    2. It converts the calculated data to a DataFrame and filters out the features with no NaN values.
    3. It adds the feature names and the data type to the DataFrame.
    4. It creates a bar plot from the DataFrame using plotly.
    5. It updates the layout and traces of the plot.
    6. If the show parameter is True, it displays the plot.
    7. It returns the created plot.
    """

    data = data.isna().sum() / len(data) * 100
    data = data.to_frame()
    data.columns = ['NaNs Percentage']
    data = data[data['NaNs Percentage'] > 0]
    data['Feature'] = data.index
    data['Data Type'] = data_type

    fig = px.bar(data, x='Feature', y='NaNs Percentage',
                 color='Feature',
                 hover_data=['NaNs Percentage'],
                 color_discrete_sequence=px.colors.qualitative.Safe,
                 text='NaNs Percentage')

    fig.update_layout(title=f'NaNs Percentage per Feature ({data_type})',
                      title_x=0.5,
                      xaxis_title='Feature',
                      yaxis_title='% of NaNs',
                      yaxis_range=[0, 100])

    fig.update_traces(textposition='outside', texttemplate='%{text:.2f}%')

    if show:
        fig.show()

    return fig


def run_all(show: bool = False) -> Generator[Figure, None, None]:
    """
    This function generates a series of plots related to the Proteins, miRNA, and mRNA datasets.

    Parameters
    ----------
    show : bool, optional
        If True, each plot is displayed as it is created. If False, the plots are not displayed. The default is False.

    Yields
    ------
    Figure
        The created plotly.graph_objs.Figure object representing the current plot.
    """

    yield plot_features_with_nans(show=show)
    yield plot_nan_percentage_per_feature(data=proteins_data, data_type='Proteins',
                                          show=show)
    yield plot_nan_percentage_per_feature(data=mirna_data, data_type='miRNA',
                                          show=show)
    yield plot_nan_percentage_per_feature(data=mrna_data, data_type='mRNA',
                                          show=show)
    yield plot_features_distribution(show=show)


def plot_features_distribution(show: bool) -> Figure:
    """
    This function creates a bar plot showing the distribution of features across the Proteins, miRNA, and mRNA datasets.

    Parameters
    ----------
    show : bool, optional
        If True, the plot is displayed. If False, the plot is not displayed. The default is False.

    Returns
    -------
    Figure
        The created plotly.graph_objs.Figure object representing the bar plot.

    The function works as follows:
    1. It calculates the total number of features in each dataset.
    2. It calculates the percentage of total features that each dataset represents.
    3. It creates a DataFrame with the calculated data.
    4. It creates a bar plot from the DataFrame using plotly.
    5. It updates the layout and traces of the plot.
    6. If the show parameter is True, it displays the plot.
    7. It returns the created plot.
    """

    proteins_features = len(proteins_data.columns)
    mirna_features = len(mirna_data.columns)
    mrna_features = len(mrna_data.columns)

    total_features = proteins_features + mirna_features + mrna_features

    data = pd.DataFrame([['Proteins', proteins_features / total_features * 100],
                         ['miRNA', mirna_features / total_features * 100],
                         ['mRNA', mrna_features / total_features * 100]],
                        columns=['Data Type', 'Features %'])

    fig = px.bar(data, x='Data Type', y='Features %', hover_data=['Features %'], text='Features %', color='Data Type',
                 color_discrete_sequence=px.colors.qualitative.Safe)

    fig.update_layout(title='Features count per source',
                      title_x=0.5,
                      xaxis_title='Source',
                      yaxis_title='Features Count')
    fig.update_traces(texttemplate='%{text:.2}%', textposition='outside')

    if show:
        fig.show()

    return fig
