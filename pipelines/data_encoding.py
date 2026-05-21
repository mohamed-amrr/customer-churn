import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

class OneHot:
    def __init__(self, X_train, X_test):
        self.X_train = X_train
        self.X_test = X_test
    
    def handle(self):
        encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        self.X_train = encoder.fit_transform(self.X_train)
        self.X_test = encoder.transform(self.X_test)
        return self.X_train, self.X_test, encoder

class Label_Encoding:
    def __init__(self, y_train, y_test):
        self.y_train = y_train
        self.y_test = y_test
    
    def handle(self):
        encoder = LabelEncoder()
        self.y_train = encoder.fit_transform(self.y_train)
        self.y_test = encoder.fit_transform(self.y_test)
        return self.y_train, self.y_test