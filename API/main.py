from fastapi import FastAPI
from pydantic import BaseModel, Field
import pickle
import mlflow.xgboost
import mlflow
import pandas as pd
import os


model = mlflow.xgboost.load_model("file:///mlflow/918679345706582571/models/m-797bc2f2e62042a0a68d56c76afcf3af/artifacts")

with open("/mlflow/918679345706582571/models/m-823ac52ffd0644a2abf9294824a38ca7/artifacts/model.pkl",
           "rb") as f:
    onehot = pickle.load(f)
app = FastAPI(title="Customer Churn Prediction")

class CustomerData(BaseModel):
    gender: str = Field(..., description="Gender (Male/Female)")
    SeniorCitizen: int = Field(..., description="Senior citizen status (0/1)")
    Partner: str = Field(..., description="Has partner (Yes/No)")
    Dependents: str = Field(..., description="Has dependents (Yes/No)")
    tenure: int = Field(..., description="Tenure in months")
    PhoneService: str = Field(..., description="Has phone service (Yes/No)")
    MultipleLines: str = Field(..., description="Multiple lines (Yes/No/No phone service)")
    InternetService: str = Field(..., description="Internet service type")
    OnlineSecurity: str = Field(..., description="Online security (Yes/No/No internet service)")
    OnlineBackup: str = Field(..., description="Online backup (Yes/No/No internet service)")
    DeviceProtection: str = Field(..., description="Device protection (Yes/No/No internet service)")
    TechSupport: str = Field(..., description="Tech support (Yes/No/No internet service)")
    StreamingTV: str = Field(..., description="Streaming TV (Yes/No/No internet service)")
    StreamingMovies: str = Field(..., description="Streaming movies (Yes/No/No internet service)")
    Contract: str = Field(..., description="Contract type")
    PaperlessBilling: str = Field(..., description="Paperless billing (Yes/No)")
    PaymentMethod: str = Field(..., description="Payment method")
    MonthlyCharges: float = Field(..., description="Monthly charges")
    TotalCharges: float = Field(..., description="Total charges")

class feature_eng:
    def transform(self, df):
        df = df.copy()

        df['AvgMonthlySpend'] = df['TotalCharges'] / (df['tenure'] + 1)
        df['ChargeRatio'] = df['MonthlyCharges'] / (df['TotalCharges'] + 1)
        df['IsNewCustomer'] = (df['tenure'] < 6).astype(int)

        return df

@app.get("/")
def root():
    return {"Welcome to api app"}

@app.post("/predict")
def predict(data: CustomerData):

    input_df = pd.DataFrame([data.model_dump()])

    input_df = feature_eng().transform(input_df)

    encoded_data = onehot.transform(input_df)

    prediction = model.predict_proba(encoded_data)

    return {
        "probability": float(prediction[0][1]),
        "prediction": "Yes" if prediction[0][1] > 0.3 else "No"
    }