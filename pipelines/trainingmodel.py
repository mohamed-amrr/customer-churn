import xgboost as xgb
from sklearn.metrics import roc_auc_score

class TrainingModel:
    model = None
    def __init__(self, X_train, X_test, y_train, y_test):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
    
    def train(self):
        xg = xgb.XGBClassifier()
        self.model = xg.fit(self.X_train, self.y_train)
        params = self.model.get_params()
        return self.model, params
    
    def calc_roc(self):
        y_pred = self.model.predict_proba(self.X_test)
        y_pred = y_pred[:, 1]
        roc = roc_auc_score(self.y_test, y_pred)
        return roc

        