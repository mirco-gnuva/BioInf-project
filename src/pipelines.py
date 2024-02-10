from pipeline_steps import (PipelineStep, IntersectDataframes, RemoveFFPESamples, FilterByNanPercentage,
                            FilterByVariance, RetainMainTumors, TruncateBarcode,
                            ComputeSNF, ComputeKMedoids, SortByIndex)
from datetime import datetime
from typing import Iterable
from loguru import logger
from models import Data


class Pipeline:
    steps: list[PipelineStep]

    def __call__(self, data: Data | list[Data], *args, **kwargs) -> Data | Iterable[Data]:
        """
        This method runs the pipeline on the given data.

        Parameters
        ----------
        data : Data | list[Data]
            The data to be processed. This can be a single Data object or a list of Data objects.

        *args
            Variable length argument list.

        **kwargs
            Arbitrary keyword arguments.

        Returns
        -------
        Data | Iterable[Data]
            The processed data. This can be a single Data object or a list of Data objects, depending on the input.

        The method works as follows:
        1. It logs the start of the pipeline execution.
        2. It records the start time of the pipeline execution.
        3. It runs the first step of the pipeline on the given data and stores the result.
        4. It iterates over the remaining steps of the pipeline, running each step on the result of the previous step and updating the result.
        5. It records the end time of the pipeline execution.
        6. It logs the duration of the pipeline execution.
        7. It returns the result of the pipeline execution.
        """

        logger.debug(f'Running {self.__class__.__name__} pipeline...')
        start = datetime.now()

        result = self.steps[0](data=data)

        for step in self.steps[1:]:
            result = step(data=result)

        end = datetime.now()
        logger.debug(f'Pipeline ran in {end - start}.')

        return result


class PhenotypePipeline(Pipeline):
    steps = [RemoveFFPESamples()]


class ExperimentPipeline(Pipeline):
    data_type: str
    steps = [RetainMainTumors(),
             FilterByNanPercentage(),
             FilterByVariance(),
             TruncateBarcode()]

    def __call__(self, data: Data | list[Data], *args, **kwargs):
        with logger.contextualize(data_type=self.data_type):
            return super().__call__(data=data, *args, **kwargs)


class miRNAPipeline(ExperimentPipeline):
    data_type = 'miRNA'


class mRNAPipeline(ExperimentPipeline):
    data_type = 'mRNA'


class ProteinsPipeline(ExperimentPipeline):
    data_type = 'Proteins'


class SubTypesPipeline(ExperimentPipeline):
    data_type = 'Subtypes'
    steps = [RetainMainTumors(),
             TruncateBarcode()]


class MultiDataframesPipeline(Pipeline):
    steps = [IntersectDataframes(),
             SortByIndex()]


class DownstreamPipeline(Pipeline):
    steps = [ComputeSNF(),
             ComputeKMedoids()]
