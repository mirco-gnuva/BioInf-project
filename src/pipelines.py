from pipeline_steps import (PipelineStep, IntersectDataframes, RemoveFFPESamples, FilterByNanPercentage,
                            FilterByVariance, RetainMainTumors, TruncateBarcode, SimilarityMatrices,
                            ComputeSNF, ComputeKMedoids, SortByIndex, ComputeMatricesAverage, MinMaxScalerStep)
from datetime import datetime
from src.models import Data
from typing import Iterable
from loguru import logger


class Pipeline:
    steps: list[PipelineStep]

    def __call__(self, data: Data | list[Data], *args, **kwargs) -> Data | Iterable[Data]:
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
