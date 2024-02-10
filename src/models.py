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


class Metric(BaseModel):
    label: str
    value: float
    range: tuple[float, float] = (0, 1)

    @property
    def normalized_value(self) -> float:
        return (self.value - self.range[0]) / (self.range[1] - self.range[0])


class RandScore(Metric):
    label: str = 'Rand Score'


class AdjustedRandScore(Metric):
    label: str = 'Adjusted Rand Score'
    range: tuple[float, float] = (-1, 1)


class NormalizedMutualInfoScore(Metric):
    label: str = 'Normalized Mutual Info Score'
    range: tuple[float, float] = (0, 1)


class SilhouetteScore(Metric):
    label: str = 'Silhouette Score'
    range: tuple[float, float] = (-1, 1)


class Metrics(BaseModel):
    label: str
    rand_score: RandScore
    adjusted_rand_score: AdjustedRandScore
    normalized_mutual_info_score: NormalizedMutualInfoScore
    silhouette_score: SilhouetteScore

    def plot(self) -> Figure:
        """Plot the metrics.

        The metrics are plotted as a Plotly bar plot.

        Returns
        -------
        Figure
            The Plotly figure.
        """

        data = self.model_dump()
        del data['label']
        data = {metric: (score['value'] - score['range'][0]) / (score['range'][1] - score['range'][0])
                for metric, score in data.items()}
        df = pd.DataFrame.from_dict(data, orient='index', columns=['value'])
        df['metric'] = df.index
        df['metric'] = df['metric'].apply(lambda x: x.replace('_', ' ').title() + 'Normalized')
        fig = px.bar(df, x='metric', y='value', title=self.label, color='metric', text='value', text_auto='.3',
                     color_discrete_sequence=px.colors.qualitative.Safe)

        ranges = self.model_dump()
        del ranges['label']
        ranges = [v['range'] for v in ranges.values()]
        ranges.sort(key=lambda x: x[1] - x[0], reverse=True)
        fig.update_layout(title_x=0.5)
        fig.update_yaxes(range=[0, 1])
        fig.update_traces(textposition='outside', textangle=0)

        return fig


class NanPercentage(BaseModel):
    column: str
    percentage: float
