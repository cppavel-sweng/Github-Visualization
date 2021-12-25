FROM python:3.6
WORKDIR /app
COPY templates ./templates
COPY app.py .
COPY requirements.txt .
COPY programming_languages.py .
COPY github_data.py .
RUN pip install -r requirements.txt