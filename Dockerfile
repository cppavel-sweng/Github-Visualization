FROM python:3.6
WORKDIR /app
COPY templates ./templates
COPY app.py .
COPY requirements.txt .
RUN pip install -r requirements.txt