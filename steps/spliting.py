from pipelines.data_splitting import DataSpliting
from zenml.steps import step

@step
def split_data(df):
    split = DataSpliting(df)
    X_train, X_test, y_train, y_test = split.handle()
    return X_train, X_test, y_train, y_test