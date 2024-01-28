from sklearn.metrics import rand_score, adjusted_rand_score, normalized_mutual_info_score

from src.models import SubtypesData, NanPercentage, Metrics
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


def get_metrics(true_labels: pd.Series, predicted_labels: pd.Series) -> Metrics:
    """Return the metrics for the given true and predicted labels.

    Parameters
    ----------
    true_labels : pd.Series
        The true labels.
    predicted_labels : pd.Series
        The predicted labels.

    Returns
    -------
    Metrics
        The metrics.
    """

    metrics = Metrics(rand_score=rand_score(true_labels, predicted_labels),
                      adjusted_rand_score=adjusted_rand_score(true_labels, predicted_labels),
                      normalized_mutual_info_score=normalized_mutual_info_score(true_labels, predicted_labels))

    return metrics
