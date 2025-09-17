"""FastAPI BFF exposing strategy and backtest endpoints."""
from __future__ import annotations

from typing import Any, Dict, List

import os

import redis
from fastapi import FastAPI
from pydantic import BaseModel, Field
from rq import Queue


class BacktestRequest(BaseModel):
    """Payload to enqueue a DSL-driven backtest job."""

    class_name: str = Field(..., max_length=64)
    dsl: Dict[str, Any]
    timeframe: str = Field(..., regex=r"^[0-9]+[smhdw]$")
    can_short: bool = False
    exchange: str
    pairs: List[str]
    backtest: Dict[str, Any]


app = FastAPI(title="Quant BFF API", version="0.1.0")
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
queue = Queue("backtests", connection=redis.from_url(redis_url))


@app.get("/healthz")
def healthcheck() -> Dict[str, str]:
    """Simple health endpoint used by Compose and monitoring."""

    return {"status": "ok"}


@app.post("/codegen-backtest")
def enqueue_codegen_backtest(payload: BacktestRequest) -> Dict[str, str]:
    """Enqueue a backtest job that generates a strategy then runs Freqtrade."""

    job = queue.enqueue("services.worker_backtest.worker.job_codegen_and_backtest", payload.dict())
    return {"job_id": job.get_id()}
