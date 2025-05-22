FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py seed_data.py ./
COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]