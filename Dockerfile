FROM python:3.6
WORKDIR /app
COPY templates ./templates
COPY backend/app.py .
COPY backend/github_data.py .
COPY backend/programming_languages.py .
COPY requirements.txt .
RUN pip install -r requirements.txt