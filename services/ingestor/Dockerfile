FROM python:3.11-slim

WORKDIR /app

COPY services/ingestor/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/ingestor /app/ingestor

CMD ["python", "-m", "ingestor.main"]
