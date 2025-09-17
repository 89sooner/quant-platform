FROM python:3.11-slim

WORKDIR /app

COPY services/worker_live/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/worker_live /app/worker_live

CMD ["python", "-m", "worker_live.worker"]
