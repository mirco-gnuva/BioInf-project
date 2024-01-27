from loguru import logger
from models import Data, PhenotypeData, mRNAData, miRNAData, ProteinsData
import pandas as pd
import os.path
import re


class FileNotValidException(Exception):
    def __init__(self, message: str):
        self.message = message


class EntryNotValidException(Exception):
    def __init__(self, message: str):
        self.message = message


class DataLoader:
    filename_regex: str
    name: str

    @logger.catch
    def check_file(self, file_path: str) -> bool:
        logger.debug(f'Checking file {file_path}...')
        file_checks = [os.path.exists(file_path),
                       os.path.isfile(file_path),
                       re.findall(self.filename_regex, file_path) != []]
        logger.debug(f'File checks: {file_checks}')

        valid_file = all(file_checks)

        if not valid_file:
            raise FileNotValidException(f'File {file_path} is not valid.')

        logger.debug(f'File {file_path} is valid.')

        return valid_file

    def load(self, file_path: str, skip_checks: bool = False) -> Data:
        logger.debug(f'Loading file {file_path}...')
        if not skip_checks:
            self.check_file(file_path)
        raw_content = self._load(file_path=file_path)
        content = self._sanitize(raw_content)
        content.name = self.name
        logger.debug(f'{file_path} loaded.')

        return content

    def _load(self, file_path: str) -> Data:
        raise NotImplementedError

    def _sanitize(self, df: pd.DataFrame) -> Data:
        raise NotImplementedError

    @staticmethod
    def get_tumor_sample(barcode: str) -> str:
        sample = barcode[13:15]

        return sample

    def is_primary_tumor(self, barcode: str) -> bool:
        sample = self.get_tumor_sample(barcode=barcode)

        return sample == '01'

    def retain_main_tumors(self, barcodes: list[str]) -> list[str]:
        main_tumors = [barcode for barcode in barcodes if self.is_primary_tumor(barcode=barcode)]

        return main_tumors


class PhenotypeDataLoader(DataLoader):
    filename_regex = r'.*mo_colData\.csv'
    name = 'clinical'

    def _load(self, file_path: str) -> PhenotypeData:
        return PhenotypeData(pd.read_csv(file_path, sep=','))

    def _sanitize(self, df: PhenotypeData) -> PhenotypeData:
        buffer = df.copy(deep=True)
        buffer = buffer.set_index('patientID')
        buffer.index.name = 'ShortPatientID'
        buffer = buffer.drop(columns=['Unnamed: 0'])
        return PhenotypeData(buffer)


class miRNADataLoader(DataLoader):
    filename_regex = r'.*miRNASeqGene.*'
    name = 'miRNA'

    def _load(self, file_path: str) -> miRNAData:
        raw = pd.read_csv(file_path, sep=',')
        raw.columns = ['ShortPatientID'] + list(raw.columns[1:])
        raw = raw.set_index('ShortPatientID')

        transposed = raw.transpose()
        return miRNAData(transposed)

    def _sanitize(self, df: miRNAData) -> miRNAData:
        return df


class mRNADataLoader(DataLoader):
    filename_regex = r'.*RNASeq2Gene.*'
    name = 'mRNA'

    def _load(self, file_path: str) -> mRNAData:
        raw = pd.read_csv(file_path, sep=',')
        raw.columns = ['ShortPatientID'] + list(raw.columns[1:])
        raw = raw.set_index('ShortPatientID')

        transposed = raw.transpose()
        return mRNAData(transposed)

    def _sanitize(self, df: mRNAData) -> mRNAData:
        return df


class ProteinsDataLoader(DataLoader):
    filename_regex = '.*RPPAArray.*'
    name = 'protein'

    def _load(self, file_path) -> ProteinsData:
        raw = pd.read_csv(file_path, sep=',')
        raw.columns = ['ShortPatientID'] + list(raw.columns[1:])
        raw = raw.set_index('ShortPatientID')

        transposed = raw.transpose()
        return ProteinsData(transposed)

    def _sanitize(self, df: ProteinsData) -> ProteinsData:
        return df
