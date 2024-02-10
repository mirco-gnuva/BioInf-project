from sklearn.metrics import rand_score, adjusted_rand_score, normalized_mutual_info_score, silhouette_score, \
    silhouette_samples
from src.models import SubtypesData, NanPercentage, Metrics, RandScore, AdjustedRandScore, \
    NormalizedMutualInfoScore, SilhouetteScore
from sklearn.preprocessing import MinMaxScaler
from plotly.graph_objs import Figure
import plotly.express as px
import pandas as pd
import numpy as np


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
    """
    This function plots the distribution of the subtypes in the given data.

    Parameters
    ----------
    data : SubtypesData
        The data containing the subtypes to be plotted.

    Returns
    -------
    Figure
        A plotly Figure object representing the distribution of the subtypes.

    The function works as follows:
    1. It first counts the occurrences of each subtype in the data using the value_counts() function.
    2. It then converts these counts into a DataFrame and renames the columns to 'Count' and 'Subtype'.
    3. A bar plot is created using plotly, with the x-axis representing the subtypes and the y-axis representing the counts.
    4. The layout of the plot is updated to place the title in the center and to place the count labels outside the bars.
    5. The Figure object representing the plot is returned.
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
    """
    This function calculates and returns the metrics for the given true and predicted labels.

    Parameters
    ----------
    true_labels : pd.Series
        The true labels of the data.
    predicted_labels : pd.Series
        The predicted labels of the data.
    similarity_data : pd.DataFrame
        The similarity data used to calculate the metrics.
    metrics_label : str
        The label for the metrics. This will be used for example as the title of the plot.

    Returns
    -------
    Metrics
        The metrics calculated from the true and predicted labels.

    The function works as follows:
    1. It first normalizes the similarity data using the MinMaxScaler.
    2. It then calculates the distances matrix from the normalized similarity data.
    3. The diagonal of the distances matrix is filled with zeros.
    4. The metrics are calculated using the true and predicted labels and the distances matrix.
    5. The calculated metrics are returned.
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
    """
    This function plots a comparison of the given metrics.

    Parameters
    ----------
    metrics : list[Metrics]
        The list of metrics to be compared. Each metric should be an instance of the Metrics class,
        which includes the label of the metric and the normalized values of the Rand score,
        Adjusted Rand score, Normalized mutual information, and Silhouette score.

    Returns
    -------
    Figure
        A plotly Figure object representing the comparison of the metrics.

    The function works as follows:
    1. It first creates a DataFrame from the given metrics, with each row representing a metric and
       each column representing a score (Rand score, Adjusted Rand score, etc.).
    2. It then rounds the values of the scores to two decimal places.
    3. The DataFrame is then reshaped (melted) to have three columns: 'Label', 'Score', and 'Value'.
    4. A grouped bar plot is created using plotly, with the x-axis representing the labels,
       the y-axis representing the values, and the color representing the scores.
    5. The layout of the plot is updated to place the title in the center, to set the range of the y-axis to [0, 1],
       and to add a dotted red line at y=0.5.
    6. The Figure object representing the plot is returned.
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
    """
    This function plots a comparison of the given metrics by score.

    Parameters
    ----------
    metrics : list[Metrics]
        The list of metrics to be compared. Each metric should be an instance of the Metrics class,
        which includes the label of the metric and the normalized values of the Rand score,
        Adjusted Rand score, Normalized mutual information, and Silhouette score.

    Returns
    -------
    Figure
        A plotly Figure object representing the comparison of the metrics by score.

    The function works as follows:
    1. It first creates a DataFrame from the given metrics, with each row representing a metric and
       each column representing a score (Rand score, Adjusted Rand score, etc.).
    2. The DataFrame is then reshaped (melted) to have three columns: 'Label', 'Score', and 'Value'.
    3. A grouped bar plot is created using plotly, with the x-axis representing the scores,
       the y-axis representing the values, and the color representing the labels.
    4. The layout of the plot is updated to place the title in the center, to set the range of the y-axis to [0, 1],
       and to add a dotted red line at y=0.5.
    5. The Figure object representing the plot is returned.
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
    """
    This function plots the silhouette scores for the given predicted labels and similarity data.

    Parameters
    ----------
    predicted_labels : array-like
        The predicted labels of the data.
    similarity_data : pd.DataFrame
        The similarity data used to calculate the silhouette scores.

    Returns
    -------
    Figure
        A plotly Figure object representing the silhouette scores.

    The function works as follows:
    1. It first normalizes the similarity data using the MinMaxScaler.
    2. It then calculates the distances matrix from the normalized similarity data.
    3. The diagonal of the distances matrix is filled with zeros.
    4. The silhouette scores are calculated using the distances matrix and the predicted labels.
    5. A DataFrame is created from the silhouette scores, with each row representing a sample and each column representing a score or a cluster.
    6. A gap is added between the clusters in the DataFrame.
    7. A bar plot is created using plotly, with the x-axis representing the samples, the y-axis representing the scores, and the color representing the scores.
    8. The layout of the plot is updated to place the title in the center, to remove the tick labels from the x-axis, and to remove the line width from the bars.
    9. The Figure object representing the plot is returned.
    """

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
    """
    This function plots a heatmap of the given similarity matrix.

    Parameters
    ----------
    similarity_matrix : pd.DataFrame
        The similarity matrix to be plotted. The index and columns of the DataFrame should represent the features,
        and the values in the DataFrame should represent the similarity between the features.
    data_type : str
        The type of the data. This will be used for example as part of the title of the plot.

    Returns
    -------
    Figure
        A plotly Figure object representing the heatmap of the similarity matrix.

    The function works as follows:
    1. It first creates a DataFrame from the similarity matrix, with each row representing a pair of features and
       each column representing a feature or a similarity.
    2. A density heatmap is created using plotly, with the x-axis representing the first feature,
       the y-axis representing the second feature, and the color representing the similarity.
    3. The layout of the plot is updated to place the title in the center, to set the titles of the axes,
       and to remove the tick labels from the axes.
    4. The colorbar of the plot is updated to set the title.
    5. The Figure object representing the plot is returned.
    """

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
