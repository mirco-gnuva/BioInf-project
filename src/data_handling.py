from loguru import logger
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

    def __init__(self, file_path: str):
        self.file_path = file_path

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

    def load(self) -> pd.DataFrame:
        logger.debug(f'Loading file {self.file_path}...')
        self.check_file(self.file_path)
        raw_content = self._load()
        content = self._sanitize(raw_content)
        logger.debug(f'{self.file_path} loaded.')

        return content

    def _load(self) -> pd.DataFrame:
        raise NotImplementedError

    def _sanitize(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError


class ClinicalDataLoader(DataLoader):
    filename_regex = r'.*mo_colData\.csv'

    def _load(self) -> pd.DataFrame:
        return pd.read_csv(self.file_path, sep=',')

    def _sanitize(self, df: pd.DataFrame) -> pd.DataFrame:
        buffer = df.copy(deep=True)
        buffer = buffer.set_index('patientID')
        buffer.index.name = 'ShortPatientID'
        buffer = buffer.drop(columns=['Unnamed: 0'])
        return buffer


class miRNADataLoader(DataLoader):
    filename_regex = r'.*miRNASeqGene.*'

    def _load(self) -> pd.DataFrame:
        raw = pd.read_csv(self.file_path, sep=',')
        raw.columns = ['ShortPatientID'] + list(raw.columns[1:])
        raw = raw.set_index('ShortPatientID')
        transposed = raw.transpose()
        transposed = transposed.rename(index=lambda x: x[:12])
        return transposed

    def _sanitize(self, df: pd.DataFrame) -> pd.DataFrame:
        return df


class mRNADataLoader(DataLoader):
    filename_regex = r'.*RNASeq2Gene.*'

    def _load(self) -> pd.DataFrame:
        raw = pd.read_csv(self.file_path, sep=',')
        raw.columns = ['ShortPatientID'] + list(raw.columns[1:])
        raw = raw.set_index('ShortPatientID')
        transposed = raw.transpose()
        transposed = transposed.rename(index=lambda x: x[:12])
        return transposed

    def _sanitize(self, df: pd.DataFrame) -> pd.DataFrame:
        return df


