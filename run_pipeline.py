from steps.cleaning import data_cleaning
from steps.encoding import encode_data
from steps.spliting import split_data
from steps.engineering import feature_eng
from steps.training import trainModel
import pandas as pd
import mlflow

mlflow.set_tracking_uri("file:///D:/Churn project/mlruns")
mlflow.set_experiment("Churn Project")

df = pd.read_csv(r"D:\\Churn project\\data\\churn_data.csv")
cleaned_data = data_cleaning(df)
data = feature_eng(cleaned_data)
X_train, X_test, y_train, y_test = split_data(data)
X_train, X_test, y_train, y_test = encode_data(X_train, X_test, y_train, y_test)
roc = trainModel(X_train, X_test, y_train, y_test)
print(f"Roc Auc accuarcy {roc}")
