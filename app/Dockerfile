FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY gui.py .

EXPOSE 8501

CMD ["streamlit", "run", "gui.py"]