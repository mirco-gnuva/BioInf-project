from sklearn.preprocessing import LabelEncoder
from sklearn.compose import ColumnTransformer
from datetime import datetime, UTC
from typing import Iterable
from loguru import logger
import pandas as pd


class PipelineStep:
    """
    Step to represent a pipeline step.
    """

    def __call__(self, data: pd.DataFrame | list[pd.DataFrame], *args, **kwargs) -> pd.DataFrame:
        """Run the pipeline step.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to process.

        Returns
        -------
        pd.DataFrame
            The processed dataframe.
        """

        logger.debug(f'Running {self.__class__.__name__}...')

        start = datetime.now(tz=UTC)
        result = self._call(data=data)
        end = datetime.now(tz=UTC)

        logger.debug(f'{self.__class__.__name__} ran in {end - start}.')

        return result

    def _call(self, data: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError


class RetainMainTumors(PipelineStep):
    """
    Step to retain only the main tumors.
    """

    def _call(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Retain only the main tumors from the given dataframe.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to filter.

        Returns
        -------
        pd.DataFrame
            The filtered dataframe.
        """

        main_tumors_samples = data.filter(regex='^TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}-01', axis=0)
        return main_tumors_samples


class RemoveFFPESamples(PipelineStep):
    """
    Step to remove FFPE samples.
    """

    def _call(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Remove FFPE samples from the given dataframe.

        That info is stored in the 'patient.samples.sample.2.is_ffpe' column.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to filter.

        Returns
        -------
        pd.DataFrame
            The filtered dataframe.
        """

        data = data[data['patient.samples.sample.2.is_ffpe'].str.lower() == 'no']
        return data


class IntersectDataframes(PipelineStep):
    """
    Step to intersect two dataframes.
    """

    def _call(self, data: Iterable[pd.DataFrame]) -> pd.DataFrame:
        """
        Intersect the passed dataframes.

        Parameters
        ----------
        data : Iterable
            The dataframes to intersect.

        Returns
        -------
        pd.DataFrame
            The intersected dataframe.
        """

        data = list(data)

        intersection = pd.concat(data, axis=1, join='inner')
        return intersection


class FilterByNanPercentage(PipelineStep):
    """
    Step to filter by NaN percentage.
    """

    def __init__(self, threshold: float = 0.1):
        self.threshold = threshold

    def _call(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Filter the given dataframe by NaN percentage.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to filter.

        Returns
        -------
        pd.DataFrame
            The filtered dataframe.
        """

        nan_counts = data.isna().sum()
        nan_percs = nan_counts / len(data)

        filtered = data[nan_percs[nan_percs <= self.threshold].index]
        return filtered


class FilterByVariance(PipelineStep):
    """
    Step to filter by variance.
    """

    def __init__(self, retain_k: int = 1000):
        self.retail_k = retain_k

    def _call(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Filter the given dataframe by variance.

        The top k features with the highest variance are retained.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to filter.

        Returns
        -------
        pd.DataFrame
            The filtered dataframe.
        """

        t = data[['ACVRL1', 'AR', 'ASNS', 'ATM', 'BRCA2', 'CDK1', 'EGFR', 'FASN', 'G6PD', 'GAPDH', 'GATA3', 'IGFBP2',
                  'INPP4B', 'IRS1', 'MYH11', 'NF2', 'PCNA', 'PDCD4', 'PDK1', 'PEA15', 'PRDX1', 'PREX1', 'PTEN', 'RBM15',
                  'TAZ', 'TFRC', 'TSC1', 'TTF1', 'VHL', 'XRCC1', 'ERCC1', 'MSH2', 'MSH6', 'XBP1']
        ]
        columns_tansformer = ColumnTransformer(transformers=[('label_encoder', LabelEncoder(), data.columns)])
        encoded_data = columns_tansformer.fit_transform(data)
        variances = encoded_data.var(axis='columns').sort_values(ascending=False)
        filtered = encoded_data[encoded_data.var(axis=1) >= self.threshold]
        return filtered


class CheckDataConsistency(PipelineStep):
    """
    Step to check data consistency.
    """

    def __init__(self, clinical_data: pd.DataFrame,
                 mirna_data: pd.DataFrame,
                 mrna_data: pd.DataFrame,
                 proteins_data: pd.DataFrame):

        self.clinical_data = clinical_data
        self.mirna_data = mirna_data
        self.mrna_data = mrna_data
        self.proteins_data = proteins_data

    def _call(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Check the consistency of the given dataframe.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to check.

        Returns
        -------
        pd.DataFrame
            The checked dataframe.
        """


