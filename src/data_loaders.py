from loguru import logger
from models import Data, PhenotypeData, mRNAData, miRNAData, ProteinsData, SubtypesData
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
        """
        This function plots a heatmap of the given similarity matrix.

        Parameters
        ----------
        similarity_matrix : pd.DataFrame
            The similarity matrix to be plotted. The index and columns of the DataFrame should represent the features,
            and the values in the DataFrame should represent the similarity between the features.
        data_type : str
            The type of the data. This will be used for example as part of the title of the plot.

        Returns
        -------
        Figure
            A plotly Figure object representing the heatmap of the similarity matrix.

        The function works as follows:
        1. It first creates a DataFrame from the similarity matrix, with each row representing a pair of features and
           each column representing a feature or a similarity.
        2. A density heatmap is created using plotly, with the x-axis representing the first feature,
           the y-axis representing the second feature, and the color representing the similarity.
        3. The layout of the plot is updated to place the title in the center, to set the titles of the axes,
           and to remove the tick labels from the axes.
        4. The colorbar of the plot is updated to set the title.
        5. The Figure object representing the plot is returned.
        """

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
        """
        This method loads the data from the given file path.

        Parameters
        ----------
        file_path : str
            The path of the file to be loaded.
        skip_checks : bool, optional
            Whether to skip the file checks. If False, the file will be checked for validity before loading.
            Default is False.

        Returns
        -------
        Data
            The loaded data.

        The method works as follows:
        1. It first logs the start of the loading process.
        2. If skip_checks is False, it checks the validity of the file using the check_file method.
        3. It then loads the raw content of the file using the _load method.
        4. The raw content is sanitized using the _sanitize method.
        5. The name of the content is set to the name of the DataLoader.
        6. It logs the end of the loading process.
        7. The sanitized content is returned.
        """

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
        """
        This function extracts the tumor sample code from the given barcode.

        Parameters
        ----------
        barcode : str
            The barcode from which the tumor sample code is to be extracted. The barcode is expected to have the tumor
            sample code at the 14th and 15th positions (0-indexed).

        Returns
        -------
        str
            The tumor sample code extracted from the barcode.

        The function works as follows:
        1. It slices the barcode at the 14th and 15th positions to get the tumor sample code.
        2. It returns the extracted tumor sample code.
        """

        sample = barcode[13:15]

        return sample

    def is_primary_tumor(self, barcode: str) -> bool:
        """
        This method determines if the given barcode corresponds to a primary tumor.

        Parameters
        ----------
        barcode : str
            The barcode to be checked. The barcode is expected to have the tumor sample code at the 14th and 15th positions (0-indexed).

        Returns
        -------
        bool
            True if the barcode corresponds to a primary tumor, False otherwise.

        The method works as follows:
        1. It first extracts the tumor sample code from the barcode using the get_tumor_sample method.
        2. It then checks if the extracted sample code is '01', which corresponds to a primary tumor.
        3. It returns the result of the check.
        """

        sample = self.get_tumor_sample(barcode=barcode)

        return sample == '01'

    def retain_main_tumors(self, barcodes: list[str]) -> list[str]:
        """
        This method filters out the barcodes that correspond to primary tumors.

        Parameters
        ----------
        barcodes : list[str]
            The list of barcodes to be filtered. Each barcode is expected to have the tumor sample code at the 14th and 15th positions (0-indexed).

        Returns
        -------
        list[str]
            The list of barcodes that correspond to primary tumors.

        The method works as follows:
        1. It iterates over the given barcodes.
        2. For each barcode, it checks if it corresponds to a primary tumor using the is_primary_tumor method.
        3. It retains the barcodes that correspond to primary tumors in a list.
        4. It returns the list of barcodes that correspond to primary tumors.
        """

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


class SubtypesDataLoader(DataLoader):
    filename_regex = 'subtypes.csv'
    name = 'subtypes'

    def _load(self, file_path) -> SubtypesData:
        raw = pd.read_csv(file_path, sep=',')
        raw.columns = ['ShortPatientID'] + list(raw.columns[1:])
        raw = raw.set_index('ShortPatientID')

        return SubtypesData(raw)

    def _sanitize(self, df: ProteinsData) -> ProteinsData:
        return df
