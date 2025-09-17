FROM python:3.11-slim

WORKDIR /app

COPY services/worker_backtest/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/worker_backtest /app/worker_backtest
COPY packages /app/packages

ENV PYTHONPATH="/app/worker_backtest:/app/packages"
ENV STRATEGIES_DIR=/app/strategies

RUN mkdir -p /app/strategies

CMD ["python", "-m", "worker_backtest.worker"]
