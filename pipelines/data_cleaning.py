import pandas as pd

class DataCleaning:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def clean_data(self) -> pd.DataFrame:
        self.df['TotalCharges'] = pd.to_numeric(self.df['TotalCharges'], errors='coerce')
        avg = self.df['TotalCharges'].mean()
        self.df['TotalCharges'].fillna(avg, inplace=True)
        self.df.drop(columns=['customerID'], inplace=True)
        return self.df