from pipeline_steps import PipelineStep, IntersectDataframes
from datetime import datetime, UTC
from loguru import logger
import pandas as pd


class Pipeline:
    steps: list[PipelineStep]

    def __call__(self, data: pd.DataFrame | list[pd.DataFrame], *args, **kwargs):
        logger.debug(f'Running {self.__class__.__name__} pipeline...')
        start = datetime.now(tz=UTC)

        result = self.steps.pop(0)(data=data)

        for step in self.steps:
            result = step(data=result)

        end = datetime.now(tz=UTC)
        logger.debug(f'Pipeline ran in {end - start}.')

        return result


class DownstreamPipeline(Pipeline):
    steps = [IntersectDataframes()]
