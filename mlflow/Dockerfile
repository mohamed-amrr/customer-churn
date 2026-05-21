FROM python:3.11

RUN pip install mlflow xgboost

RUN mkdir /mlflow

EXPOSE 5000

CMD ["mlflow", "server", \
     "--host", "0.0.0.0", \
     "--port", "5000", \
     "--backend-store-uri", "/mlflow", \
     "--default-artifact-root", "/mlflow"]