# 🔄 Customer Churn Prediction — End-to-End MLOps Pipeline

> An end-to-end machine learning system that predicts customer churn using a production-ready MLOps stack with experiment tracking, containerization, and an interactive GUI.

---

## 📌 Project Overview

Customer churn is one of the most costly problems for subscription-based businesses. This project builds a **full MLOps pipeline** — from raw data ingestion to a deployed prediction API — to identify customers likely to churn, enabling proactive retention strategies.

---

## 🏗️ Architecture

```
Raw Data
   │
   ▼
Data Pipeline (preprocessing, feature engineering)
   │
   ▼
MLflow Experiment Tracking ──► Model Registry
   │
   ▼
Trained Model
   │
   ├──► FastAPI REST API
   │         │
   │         ▼
   │     GUI (Web Interface)
   │
   └──► Docker Container (reproducible deployment)
```

---

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| **API** | FastAPI |
| **ML Pipeline** | Scikit-learn Pipelines |
| **Experiment Tracking** | MLflow |
| **GUI** | Streamlit / Gradio *(update as needed)* |
| **Containerization** | Docker |
| **Language** | Python 3.11 |
| **Data Processing** | Pandas, NumPy |
| **Modeling** | Scikit-learn, XGBoost *(update as needed)* |
| **Visualization** | Matplotlib, Seaborn |

---

## ✨ Features

- ✅ **End-to-end ML pipeline** — data ingestion → preprocessing → training → evaluation
- ✅ **MLflow tracking** — logs metrics, parameters, and artifacts for every experiment run
- ✅ **Model Registry** — version-controlled model management via MLflow
- ✅ **FastAPI backend** — RESTful API for real-time churn predictions
- ✅ **Interactive GUI** — user-friendly interface to input customer data and get predictions
- ✅ **Dockerized** — fully containerized for consistent, reproducible environments

---

## 📁 Project Structure

```
customer-churn/
│
├── data/
│   ├── raw/                  # Raw dataset
│   └── processed/            # Cleaned & engineered features
│
├── notebooks/
│   └── EDA.ipynb             # Exploratory data analysis
│
├── src/
│   ├── pipeline.py           # Scikit-learn preprocessing + training pipeline
│   ├── train.py              # Model training with MLflow logging
│   ├── predict.py            # Prediction logic
│   

├── api/
│   └── main.py               # FastAPI application
│
├── gui/
│   └── app.py                # GUI application
│
├── mlruns/                   # MLflow experiment logs (auto-generated)
├── Dockerfile                # Docker configuration
├── requirements.txt          # Python dependencies
└── README.md
```

---

## ⚙️ Getting Started

### Prerequisites

- Python 3.8+
- Docker

### 1. Clone the Repository

```bash
git clone https://github.com/mohamed-amrr/customer-churn.git
cd customer-churn
```

### 2. Run with Docker (Recommended)

```bash
# Build the image
docker build -t customer-churn .

# Run the container
docker run -p 8000:8000 customer-churn
```

### 3. Run Locally (without Docker)

```bash
pip install -r requirements.txt

# Train the model
python src/train.py

# Start the API
uvicorn api.main:app --reload

# Launch the GUI
python gui/app.py
```

---

## 📊 MLflow Experiment Tracking

```bash
# Launch the MLflow UI
mlflow ui

# Open in browser
http://localhost:5000
```

Track and compare experiments including:
- Model accuracy, precision, recall, F1-score, AUC-ROC
- Hyperparameters for each run
- Saved model artifacts

---

## 🌐 API Usage

Once the FastAPI server is running, visit:

- **Swagger docs:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Example Request

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "tenure": 12,
    "monthly_charges": 65.5,
    "total_charges": 786.0,
    "contract_type": "Month-to-month"
  }'
```

### Example Response

```json
{
  "churn_prediction": 1,
  "churn_probability": 0.83,
  "message": "High risk of churn"
}
```

---

## 🔍 Key ML Pipeline Steps

1. **Data Cleaning** — handle missing values, duplicates, type casting
2. **Feature Engineering** — encode categoricals, scale numerics
3. **Scikit-learn Pipeline** — chained transformers + classifier in one object
4. **MLflow Logging** — auto-logs params, metrics, and model artifact per run
5. **Model Selection** — compare runs in MLflow UI, register best model
6. **Serving** — load registered model in FastAPI for inference

---

## 👤 Author

**Mohamed Amr**
Faculty of Engineering, New Ismailia University
- GitHub: [@yourusername](https://github.com/mohamed-amrr)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
