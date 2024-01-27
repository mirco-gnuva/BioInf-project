from sklearn.preprocessing import LabelEncoder
from sklearn.compose import ColumnTransformer
from datetime import datetime, timezone
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

        start = datetime.now()
        result = self._call(data=data)
        end = datetime.now()

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

        data = data[data['clinical_patient.samples.sample.2.is_ffpe'].str.lower() == 'no']
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

        data_copy = [df.copy() for df in data]
        for name, df in zip([df.name for df in data], data_copy):
            df.columns = [f'{name}_{col}' for col in df.columns]

        intersection = pd.concat(data_copy, axis=1, join='inner')
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
        self.retain_k = retain_k

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

        encoded_data = EncodeCategoricalData()(data=data)
        variances = encoded_data.var(axis='rows').sort_values(ascending=False)
        filtered = data[variances[:self.retain_k].index]
        return filtered


class EncodeCategoricalData(PipelineStep):
    """
    Step to encode categorical data.
    """

    def _call(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Encode the categorical data of the given dataframe.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to encode.

        Returns
        -------
        pd.DataFrame
            The encoded dataframe.
        """

        encoded_data = data.copy(deep=True)

        for col in [col for col in encoded_data.columns if encoded_data[col].dtype in ['string', 'category']]:
            encoded_data[col] = LabelEncoder().fit_transform(encoded_data[col])
        return encoded_data


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

        pass


class CastDataTypes(PipelineStep):
    """
    Step to cast data types.
    """

    def _call(self, data: pd.DataFrame) -> pd.DataFrame:
        """Cast the data types of the given dataframe.

        This step assumes that all columns with dtype 'object' are strings and no nan is present.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to cast.

        Returns
        -------
        pd.DataFrame
            The cast dataframe.
        """

        data_copy = data.copy(deep=True)
        for col in [col for col in data_copy.columns if data_copy[col].dtype == 'object']:
            data_copy[col] = data_copy[col].astype('string')
        return data_copy
