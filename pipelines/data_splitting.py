from sklearn.model_selection import train_test_split
import pandas as pd

class DataSpliting:
    def __init__(self, df:pd.DataFrame):
        self.df = df
    
    def handle(self):
        X = self.df.drop(columns=['Churn'], axis=1)
        y = self.df['Churn']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        return X_train, X_test, y_train, y_test