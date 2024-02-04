from sklearn.metrics import rand_score, adjusted_rand_score, normalized_mutual_info_score
from src.models import SubtypesData, NanPercentage, Metrics, Metric, RandScore, AdjustedRandScore, \
    NormalizedMutualInfoScore
from plotly.graph_objs import Figure
import plotly.express as px
import pandas as pd


def get_nan_percentage(data: pd.DataFrame) -> list[NanPercentage]:
    """Return the percentage of NaN values for each column in the given dataframe.

    Parameter
    ---------
    data : pd.DataFrame
        The dataframe to analyze.

    Returns
    -------
    list[NanPercentage]
        The list of NanPercentage objects.
    """

    nan_counts = list(zip(data.columns, data.isna().sum()))

    nan_percs = [NanPercentage(column=col, percentage=count / len(data))
                 for col, count in nan_counts]

    return nan_percs


def get_subtypes_distribution(data: SubtypesData) -> pd.Series:
    """Return the distribution of subtypes in the given dataframe.

    Parameters
    ----------
    data : SubtypesData
        The dataframe to analyze.

    Returns
    -------
    pd.Series
        The distribution of subtypes.
    """
    counts = data.groupby(['Subtype_Integrative']).count()[data.columns[0]]
    counts.name = 'count'

    return counts


def get_metrics(true_labels: pd.Series, predicted_labels: pd.Series, metrics_label: str) -> Metrics:
    """Return the metrics for the given true and predicted labels.

    Parameters
    ----------
    true_labels : pd.Series
        The true labels.
    predicted_labels : pd.Series
        The predicted labels.
    metrics_label : str
        The label for the metrics. Will be used for example as the title of the plot.

    Returns
    -------
    Metrics
        The metrics.
    """

    metrics = Metrics(rand_score=RandScore(value=rand_score(true_labels, predicted_labels)),
                      adjusted_rand_score=AdjustedRandScore(value=adjusted_rand_score(true_labels, predicted_labels)),
                      normalized_mutual_info_score=NormalizedMutualInfoScore(
                          value=normalized_mutual_info_score(true_labels, predicted_labels)),
                      label=metrics_label)

    return metrics


def get_metrics_comparison_plot(metrics: list[Metrics]) -> Figure:
    """Plot the metrics comparison.

    Parameters
    ----------
    metrics : list[Metrics]
        The list of metrics to plot.
    """

    data = pd.DataFrame([{'Label': m.label,
                          'Rand score (norm.)': m.rand_score.normalized_value,
                          'Adjusted Rand score (norm.)': m.adjusted_rand_score.normalized_value,
                          'Nromalized mutual information (norm.)': m.normalized_mutual_info_score.normalized_value}
                         for m in metrics])

    for col in [col for col in data.columns if data[col].dtype == 'float64']:
        data[col] = data[col].apply(lambda x: round(x, 2))

    melt_data = data.melt(id_vars=['Label'])
    melt_data.columns = ['Label', 'Score', 'Value']

    fig = px.bar(melt_data,
                 x='Label',
                 y='Value',
                 color='Score',
                 barmode='group',
                 color_discrete_sequence=px.colors.qualitative.Safe)
    fig.update_layout(title='Metrics comparison',
                      title_x=0.5,
                      xaxis_title='Score',
                      yaxis_title='Value',
                      yaxis_range=[0, 1])

    return fig


def get_metrics_comparison_by_score_plot(metrics: list[Metrics]) -> Figure:
    """Plot the metrics comparison.

    Parameters
    ----------
    metrics : list[Metrics]
        The list of metrics to plot.
    """

    data = pd.DataFrame([{'Label': m.label,
                          'Rand score (norm.)': m.rand_score.normalized_value,
                          'Adjusted Rand score (norm.)': m.adjusted_rand_score.normalized_value,
                          'Nromalized mutual information (norm.)': m.normalized_mutual_info_score.normalized_value}
                         for m in metrics])

    melt_data = data.melt(id_vars=['Label'])
    melt_data.columns = ['Label', 'Score', 'Value']

    fig = px.bar(melt_data,
                 x='Score',
                 y='Value',
                 color='Label',
                 barmode='group',
                 color_discrete_sequence=px.colors.qualitative.Safe)

    fig.update_layout(title='Metrics comparison by score',
                      title_x=0.5,
                      xaxis_title='Score',
                      yaxis_title='Value',
                      yaxis_range=[0, 1])

    return fig
