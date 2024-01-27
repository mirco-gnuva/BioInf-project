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
