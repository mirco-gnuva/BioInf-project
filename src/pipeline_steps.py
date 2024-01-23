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

        data = data[data['patient.samples.sample.2.is_ffpe'] == 'NO']
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
