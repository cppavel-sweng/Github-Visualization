FROM python:3.6
WORKDIR /app
COPY templates ./templates
COPY backend .
COPY requirements.txt .
RUN pip install -r requirements.txt