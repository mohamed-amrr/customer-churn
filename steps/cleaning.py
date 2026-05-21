from pipelines.data_cleaning import DataCleaning
from zenml.steps import step
import pandas as pd

@step
def data_cleaning(df:pd.DataFrame) -> pd.DataFrame:
    clean = DataCleaning(df)
    cleaned_data = clean.clean_data()
    return cleaned_data
