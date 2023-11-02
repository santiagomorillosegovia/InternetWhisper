FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY main.py .

CMD ["streamlit", "run", "main.py" ,"--server.port=80", "--server.address=0.0.0.0"]