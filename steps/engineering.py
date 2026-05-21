from pipelines.feature_engineering import FeatureEngineering
from zenml.steps import step

@step
def feature_eng(df):
    new = FeatureEngineering(df)
    data = new.handle()
    return data