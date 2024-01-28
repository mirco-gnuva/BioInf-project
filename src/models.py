from plotly.graph_objs import Figure
from pydantic import BaseModel
import plotly.express as px
from typing import Union
import pandas as pd


class AbstractData(pd.DataFrame):
    name: str

    def __hash__(self):
        return id(self)


class ProteinsData(AbstractData):
    name = 'Proteins'


class mRNAData(AbstractData):
    name = 'mRNA'


class miRNAData(AbstractData):
    name = 'miRNA'


class PhenotypeData(AbstractData):
    name = 'Phenotype'


class SubtypesData(AbstractData):
    name = 'Subtypes'


Data = Union[ProteinsData, mRNAData, miRNAData]


class Metrics(BaseModel):
    rand_score: float
    adjusted_rand_score: float
    normalized_mutual_info_score: float

    def plot(self) -> Figure:
        """Plot the metrics.

        The metrics are plotted as a Plotly bar plot.

        Returns
        -------
        Figure
            The Plotly figure.
        """

        df = pd.DataFrame.from_dict(self.model_dump(), orient='index', columns=['value'])
        df['metric'] = df.index
        fig = px.bar(df, x='metric', y='value', title='Metrics', color='metric')
        fig.update_layout(title_x=0.5)

        return fig


class NanPercentage(BaseModel):
    column: str
    percentage: float
