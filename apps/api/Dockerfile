FROM python:3.11-slim

WORKDIR /app

COPY apps/api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/api /app/app
COPY packages /app/packages
COPY services /app/services

ENV PYTHONPATH="/app/app:/app/packages:/app/services"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
