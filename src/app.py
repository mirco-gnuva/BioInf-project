from data_handling import DataLoader, ClinicalDataLoader, miRNADataLoader, mRNADataLoader, ProteinsDataLoader
import streamlit as st
import pandas as pd


st.title('Bioinformatics Project - Mirco Gnuva')


def data_uploader(data_loader: DataLoader) -> pd.DataFrame:
    file = st.file_uploader(f'Upload {data_loader.__class__.__name__} data')
    if file is not None:
        df = data_loader.load(file)
        return df


data_uploader(data_loader=ClinicalDataLoader())




st.file_uploader('Upload clinical data')
st.file_uploader('Upload proteins data')
st.file_uploader('Upload miRNA data')
st.file_uploader('Upload mRNA data')
