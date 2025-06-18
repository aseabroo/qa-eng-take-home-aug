FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py seed_data.py ./
COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/

# Copy test file for API testing
COPY test_api.py ./
COPY pytest.ini ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]