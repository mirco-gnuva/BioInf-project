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

    def load(self, file_path: str, skip_checks: bool = False) -> pd.DataFrame:
        logger.debug(f'Loading file {file_path}...')
        if not skip_checks:
            self.check_file(file_path)
        raw_content = self._load(file_path=file_path)
        content = self._sanitize(raw_content)
        logger.debug(f'{file_path} loaded.')

        return content

    def _load(self, file_path: str) -> pd.DataFrame:
        raise NotImplementedError

    def _sanitize(self, df: pd.DataFrame) -> pd.DataFrame:
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


class ClinicalDataLoader(DataLoader):
    filename_regex = r'.*mo_colData\.csv'

    def _load(self, file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path, sep=',')

    def _sanitize(self, df: pd.DataFrame) -> pd.DataFrame:
        buffer = df.copy(deep=True)
        buffer = buffer.set_index('patientID')
        buffer.index.name = 'ShortPatientID'
        buffer = buffer.drop(columns=['Unnamed: 0'])
        return buffer


class miRNADataLoader(DataLoader):
    filename_regex = r'.*miRNASeqGene.*'

    def _load(self, file_path: str) -> pd.DataFrame:
        raw = pd.read_csv(file_path, sep=',')
        raw.columns = ['ShortPatientID'] + list(raw.columns[1:])
        raw = raw.set_index('ShortPatientID')

        main_tumors = self.retain_main_tumors(barcodes=raw.columns)
        raw = raw[main_tumors]

        transposed = raw.transpose()
        transposed = transposed.rename(index=lambda x: x[:12])
        return transposed

    def _sanitize(self, df: pd.DataFrame) -> pd.DataFrame:
        return df


class mRNADataLoader(DataLoader):
    filename_regex = r'.*RNASeq2Gene.*'

    def _load(self, file_path: str) -> pd.DataFrame:
        raw = pd.read_csv(file_path, sep=',')
        raw.columns = ['ShortPatientID'] + list(raw.columns[1:])
        raw = raw.set_index('ShortPatientID')

        main_tumors = self.retain_main_tumors(barcodes=raw.columns)
        raw = raw[main_tumors]

        transposed = raw.transpose()
        transposed = transposed.rename(index=lambda x: x[:12])
        return transposed

    def _sanitize(self, df: pd.DataFrame) -> pd.DataFrame:
        return df


class ProteinsDataLoader(DataLoader):
    filename_regex = '.*RPPAArray.*'

    def _load(self, file_path) -> pd.DataFrame:
        raw = pd.read_csv(file_path, sep=',')
        raw.columns = ['ShortPatientID'] + list(raw.columns[1:])
        raw = raw.set_index('ShortPatientID')

        main_tumors = self.retain_main_tumors(barcodes=raw.columns)
        raw = raw[main_tumors]

        transposed = raw.transpose()
        transposed = transposed.rename(index=lambda x: x[:12])

        return transposed

    def _sanitize(self, df: pd.DataFrame) -> pd.DataFrame:
        return df
