import numpy as np
from sklearn.metrics import rand_score, adjusted_rand_score, normalized_mutual_info_score, silhouette_score, \
    silhouette_samples
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm

from src.models import SubtypesData, NanPercentage, Metrics, Metric, RandScore, AdjustedRandScore, \
    NormalizedMutualInfoScore, SilhouetteScore
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


def plot_subtypes_distribution(data: SubtypesData) -> Figure:
    """Plot the distribution of the subtypes.

    """
    counts = data['Subtype_Integrative'].value_counts()
    counts = pd.DataFrame(counts)
    counts.columns = ['Count']
    counts['Subtype'] = counts.index.astype(str)

    fig = px.bar(counts, x='Subtype', y='Count', title='Subtypes distribution',
                 labels={'x': 'Subtype', 'y': 'Count'}, color_discrete_sequence=px.colors.qualitative.Safe,
                 color='Subtype', text='Count')
    fig.update_layout(title_x=0.5)
    fig.update_traces(textposition='outside', textangle=0)

    return fig


def get_metrics(true_labels: pd.Series, predicted_labels: pd.Series, similarity_data: pd.DataFrame,
                metrics_label: str) -> Metrics:
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

    scaler = MinMaxScaler()
    normalized_similarity = scaler.fit_transform(similarity_data)

    distances_matrix = pd.DataFrame(1 - normalized_similarity).values

    np.fill_diagonal(distances_matrix, 0)
    metrics = Metrics(rand_score=RandScore(value=rand_score(true_labels, predicted_labels)),
                      adjusted_rand_score=AdjustedRandScore(value=adjusted_rand_score(true_labels, predicted_labels)),
                      normalized_mutual_info_score=NormalizedMutualInfoScore(
                          value=normalized_mutual_info_score(true_labels, predicted_labels)),
                      silhouette_score=SilhouetteScore(value=silhouette_score(distances_matrix, predicted_labels,
                                                                              random_state=5, metric='precomputed')),
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
                          'Normalized mutual information (norm.)': m.normalized_mutual_info_score.normalized_value,
                          'Silhouette score (norm.)': m.silhouette_score.normalized_value}
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

    fig.add_hline(y=0.5, line_dash="dot", line_color="red")

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
                          'Normalized mutual information (norm.)': m.normalized_mutual_info_score.normalized_value,
                          'Silhouette score (norm.)': m.silhouette_score.normalized_value}
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

    fig.add_hline(y=0.5, line_dash="dot", line_color="red")

    return fig


def get_silhouette_score_plot(predicted_labels, similarity_data: pd.DataFrame) -> Figure:
    scaler = MinMaxScaler()
    normalized_similarity = scaler.fit_transform(similarity_data)

    distances_matrix = pd.DataFrame(1 - normalized_similarity).values

    np.fill_diagonal(distances_matrix, 0)

    scores = silhouette_samples(distances_matrix, predicted_labels)
    data = pd.DataFrame({'Sample': range(len(scores)), 'Score': scores, 'Cluster': predicted_labels})

    gapped_data = pd.DataFrame()
    gap_lines_n = 10
    gap = pd.DataFrame({'Sample': [-1] * gap_lines_n, 'Score': [0] * gap_lines_n, 'Cluster': [-1] * gap_lines_n})
    for cluster in sorted(data['Cluster'].unique()):
        cluster_data = data[data['Cluster'] == cluster]
        cluster_data = pd.concat([cluster_data, gap]).reset_index(drop=True)

        gapped_data = pd.concat([gapped_data, cluster_data]).reset_index(drop=True)

    fig = px.bar(gapped_data, x=gapped_data.index, y='Score', title='Silhouette scores', color='Score',
                 hover_data=['Cluster'])
    fig.update_layout(title_x=0.5, bargap=0)
    fig.update_traces(marker_line_width=0)
    fig.update_xaxes(showticklabels=False, title=None)

    return fig


def plot_similarity_heatmap(similarity_matrix: pd.DataFrame, data_type: str) -> Figure:
    df = pd.DataFrame(({'Feature 1': similarity_matrix.index[i],
                        'Feature 2': similarity_matrix.columns[j],
                        'Similarity': similarity_matrix.iloc[i, j]}
                       for i in range(len(similarity_matrix))
                       for j in range(len(similarity_matrix))),
                      columns=['Feature 1', 'Feature 2', 'Similarity'])

    fig = px.density_heatmap(df, x='Feature 1', y='Feature 2', z='Similarity')

    fig.update_layout(title=f'Features similarity ({data_type})',
                      title_x=0.5,
                      xaxis_title='Feature',
                      yaxis_title='Feature')

    fig.update_coloraxes(colorbar_title='Similarity')
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    return fig
