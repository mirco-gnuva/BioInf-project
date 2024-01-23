from pydantic import BaseModel
import pandas as pd


class NanPercentage(BaseModel):
    column: str
    percentage: float


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
