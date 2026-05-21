from pipelines.data_encoding import OneHot, Label_Encoding
from zenml.steps import step
import mlflow

@step
def encode_data(X_train, X_test, y_train, y_test):

    with mlflow.start_run(run_name="Data Encoding") as run:  
        onehot = OneHot(X_train, X_test)
        X_train, X_test, model = onehot.handle()
        label = Label_Encoding(y_train, y_test)
        y_train, y_test = label.handle()
        mlflow.sklearn.log_model(model, artifact_path="onehot_encoder")
    return X_train, X_test, y_train, y_test