from pipelines.trainingmodel import TrainingModel
from zenml.steps import step
import xgboost as xgb
import mlflow

@step
def trainModel(X_train, X_test, y_train, y_test):

    with mlflow.start_run(run_name="Training Model") as run:
        m = TrainingModel(X_train, X_test, y_train, y_test)
        model, params = m.train()
        roc = m.calc_roc()
        mlflow.log_metric("Roc Auc Score", roc)
        mlflow.log_params(params)
        mlflow.xgboost.log_model(model, artifact_path="Xgboost_Model")
    return roc