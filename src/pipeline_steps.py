from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.cluster import SpectralClustering
from sklearn_extra.cluster import KMedoids
from datetime import datetime
from itertools import chain
from typing import Iterable
from models import Data
from tqdm.auto import tqdm
from loguru import logger
from snf import compute
import pandas as pd
import numpy as np
import snf.compute


class PipelineStep:
    """
    Step to represent a pipeline step.
    """

    def __call__(self, data: Data | list[Data], *args, **kwargs) -> Data | list[Data]:
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

        return [df.__class__(df) for df in result] if isinstance(data, list) else data.__class__(result)

    def _call(self, data: Data) -> Data:
        raise NotImplementedError


class RetainMainTumors(PipelineStep):
    """
    Step to retain only the main tumors.
    """

    def _call(self, data: Data) -> Data:
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

        logger.debug('Retaining main tumor samples only...')
        main_tumors_samples = data.filter(regex='^TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}-01', axis='index')
        logger.debug(f'Main tumor samples: {len(main_tumors_samples)}/{len(data)}')
        return main_tumors_samples


class RemoveFFPESamples(PipelineStep):
    """
    Step to remove FFPE samples.
    """

    def _call(self, data: Data) -> Data:
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

        logger.debug('Removing FFPE samples...')
        no_ffpe_data = data[data['patient.samples.sample.2.is_ffpe'].str.lower() == 'no']

        samples_removed_n = len(data) - len(no_ffpe_data)

        logger.log('DEBUG' if not samples_removed_n else 'WARNING',
                   f'FFPE samples removed: {samples_removed_n}/{len(data)}')
        return no_ffpe_data


class IntersectDataframes(PipelineStep):
    """
    Step to intersect two dataframes.
    """

    def _call(self, data: Iterable[Data]) -> list[Data]:
        """
        Intersect the passed dataframes.

        Parameters
        ----------
        data : Iterable
            The dataframes to intersect.

        Returns
        -------
        list[pd.DataFrame]
            The intersected dataframes.
        """

        logger.debug('Intersecting dataframes...')
        data_copy = [df.copy() for df in data]

        indexes = [list(df.index) for df in data_copy]
        candidates = set(chain(*indexes))

        index = [c for c in candidates if all(c in idx for idx in indexes)]

        data_copy = [cls(data.reindex(index=index)) for cls, data in zip([df.__class__ for df in data], data_copy)]

        resume = '\n\t'.join(
            [f'{len(intersected)}/{len(original)}' for original, intersected in zip(data, data_copy)])

        logger.debug(f'Dataframes intersected, preserved: \n\t{resume}')

        return data_copy


class FilterByNanPercentage(PipelineStep):
    """
    Step to filter by NaN percentage.
    """

    def __init__(self, threshold: float = 0):
        self.threshold = threshold

    def _call(self, data: Data) -> Data:
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

        logger.debug(f'Filtering by NaN percentage (threshold: {self.threshold})...')
        nan_counts = data.isna().sum()
        nan_percs = nan_counts / len(data)

        filtered = data[nan_percs[nan_percs <= self.threshold].index]
        filtered_out_n = len(data) - len(filtered)
        logger.log('DEBUG' if not filtered_out_n else 'WARNING',
                   f'Samples filtered out: {len(data) - len(filtered)}/{len(data)}')

        return filtered


class FilterByVariance(PipelineStep):
    """
    Step to filter by variance.
    """

    def __init__(self, retain_k: int = 100):
        self.retain_k = retain_k

    def _call(self, data: Data) -> Data:
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

    def _call(self, data: Data) -> Data:
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

        logger.debug('Encoding categorical data...')
        encoded_data = data.copy(deep=True)

        categorical_columns = [col for col in encoded_data.columns
                               if encoded_data[col].dtype in ['object', 'string', 'category', ]]

        for col in categorical_columns:
            encoded_data[col] = LabelEncoder().fit_transform(encoded_data[col])

        logger.debug(f'{len(categorical_columns)} categorical columns encoded.')

        return encoded_data


class CheckDataConsistency(PipelineStep):
    """
    Step to check data consistency.
    """

    def __init__(self, clinical_data: Data,
                 mirna_data: Data,
                 mrna_data: Data,
                 proteins_data: Data):
        self.clinical_data = clinical_data
        self.mirna_data = mirna_data
        self.mrna_data = mrna_data
        self.proteins_data = proteins_data

    def _call(self, data: Data) -> Data:
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

    def _call(self, data: Data) -> Data:
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


class TruncateBarcode(PipelineStep):
    """
    Step to truncate the barcode.
    """

    def _call(self, data: Data) -> Data:
        """Truncate the barcode of the given dataframe.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to truncate.

        Returns
        -------
        pd.DataFrame
            The truncated dataframe.
        """

        data_copy = data.copy(deep=True)
        data_copy.index = data_copy.index.str[:12]
        return data_copy


class ZScoreScaler(PipelineStep):
    """
    Step to scale the data using the Z-score.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scaler = StandardScaler()

    def _call(self, data: Data) -> Data:
        """Scale the data using the Z-score.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to scale.

        Returns
        -------
        pd.DataFrame
            The scaled dataframe.
        """

        data_copy = data.copy(deep=True)
        for col in tqdm(data_copy.columns, desc='Scaling data', leave=False):
            data_copy[col] = self.scaler.fit_transform(data_copy[col].values.reshape(-1, 1))

        return data_copy


class MinMaxScalerStep(PipelineStep):
    """
    Step to scale the data using the MinMaxScaler.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scaler = MinMaxScaler()

    def _call(self, data: Data) -> Data:
        """Scale the data using the MinMaxScaler.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to scale.

        Returns
        -------
        pd.DataFrame
            The scaled dataframe.
        """

        data_copy = data.copy(deep=True)
        for col in tqdm(data_copy.columns, desc='Scaling data', leave=False):
            data_copy[col] = self.scaler.fit_transform(data_copy[col].values.reshape(-1, 1))

        return data_copy


class SimilarityMatrices(PipelineStep):
    """
    Step to compute the similarity matrix.
    """

    def _call(self, data: list[Data]) -> list[pd.DataFrame]:
        """Compute the similarity matrix of the given dataframe.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to process.

        Returns
        -------
        pd.DataFrame
            The similarity matrix.
        """

        logger.debug(f'Computing similarity matrix...')
        encoder = EncodeCategoricalData()
        encoded_data = [encoder(d) for d in data]

        scalser = ZScoreScaler()
        scaled_data = [scalser(d) for d in encoded_data]

        matrices = compute.make_affinity(scaled_data, K=20, normalize=False)
        index = data[0].index
        similarity_matrix = [pd.DataFrame(matrix, index=index, columns=index) for matrix in matrices]
        logger.debug('Similarity matrix computed.')

        return similarity_matrix


class DownstreamStep:
    """
        Step to represent a pipeline step.
        """

    def __call__(self, data: Data | list[Data], *args, **kwargs) -> Data | list[Data]:
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
        result = self._call(data=data, *args, **kwargs)
        end = datetime.now()

        logger.debug(f'{self.__class__.__name__} ran in {end - start}.')

        return result

    def _call(self, data: Data, *args, **kwargs) -> Data:
        raise NotImplementedError


class ComputeMatricesAverage(DownstreamStep):
    """
    Step to compute the similarity matrix.
    """

    def _call(self, data: list[pd.DataFrame], *args, **kwargs) -> pd.DataFrame:
        """Compute the similarity matrix of the given dataframe.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to process.

        Returns
        -------
        pd.DataFrame
            The similarity matrix.
        """

        logger.debug('Computing average...')

        arrays = [df.to_numpy() for df in data]
        stack = np.dstack(arrays)
        average = np.mean(stack, axis=2)

        result = pd.DataFrame(average, index=data[0].index, columns=data[0].index)

        logger.debug('Average computed.')

        return result


class ComputeSNF(DownstreamStep):
    """
    Step to compute the similarity matrix.
    """

    def _call(self, data: list[pd.DataFrame], *args, **kwargs) -> pd.DataFrame:
        """Compute the similarity matrix of the given dataframe.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to process.

        Returns
        -------
        pd.DataFrame
            The similarity matrix.
        """

        logger.debug('Computing SNF...')

        fusion = snf.compute.snf(data, K=20, t=20)
        result = pd.DataFrame(fusion, index=data[0].index, columns=data[0].index)

        logger.debug('SNF computed.')

        return result


class ComputeKMedoids(DownstreamStep):
    """
    Step to compute the similarity matrix.
    """

    def _call(self, data: pd.DataFrame, clusters_n: int = 3, *args, **kwargs) -> pd.Series:
        """Compute the similarity matrix of the given dataframe.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to process.
        clusters_n : int
            The number of clusters to be detected.

        Returns
        -------
        pd.DataFrame
            The similarity matrix.
        """

        logger.debug('Computing KMedoids...')
        scaler = MinMaxScaler()
        normalized_similarity = scaler.fit_transform(data)
        distances = scaler.fit_transform(1 - normalized_similarity)

        clusters = KMedoids(n_clusters=clusters_n, random_state=0, metric='precomputed', method='pam').fit_predict(distances)
        clusters = pd.Series(clusters, index=data.index)

        logger.debug('Clustering computed.')

        return clusters


class ComputeSpectralClustering(DownstreamStep):
    """
    Step to compute the similarity matrix.
    """

    def _call(self, data: pd.DataFrame, clusters_n: int = 3, *args, **kwargs) -> pd.Series:
        """Compute the similarity matrix of the given dataframe.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to process.
        clusters_n : int
            The number of clusters to be detected.

        Returns
        -------
        pd.DataFrame
            The similarity matrix.
        """

        logger.debug('Computing Spectral Clustering...')

        clusters = SpectralClustering(n_clusters=clusters_n, affinity='precomputed', n_neighbors=20).fit_predict(data)
        clusters = pd.Series(clusters, index=data.index)

        logger.debug('Clustering computed.')

        return clusters


class SortByIndex(PipelineStep):
    """
    Step to sort by index.
    """

    def _call(self, data: Data | list[Data], *args, **kwargs) -> Data | list[Data]:
        """Sort the given dataframe by index.

        Parameters
        ----------
        data : pd.DataFrame
            The dataframe to sort.

        Returns
        -------
        pd.DataFrame
            The sorted dataframe.
        """

        data_sorted = data.__class__(data.sort_index()) if isinstance(data, Data) else [df.__class__(df.sort_index())
                                                                                        for df in data]

        return data_sorted
