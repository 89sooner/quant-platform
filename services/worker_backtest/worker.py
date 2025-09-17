"""RQ worker entry-point for code generation and backtesting."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

import redis
from dotenv import load_dotenv
from rq import Connection, Queue, Worker

from .backtest_runner import run_backtest_pipeline
from .codegen import render_strategy, write_strategy_file

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
STRATEGIES_DIR = Path(os.getenv("STRATEGIES_DIR", "/app/strategies"))


def job_codegen_and_backtest(payload: Dict) -> Dict[str, str]:
    class_name = payload["class_name"]
    strategy_code = render_strategy(payload["dsl"], class_name, payload["timeframe"], payload.get("can_short", False))
    strategy_path = write_strategy_file(strategy_code, STRATEGIES_DIR, class_name)
    results = run_backtest_pipeline(payload)
    results.update({"strategy_file": str(strategy_path)})
    return results


def main() -> None:
    connection = redis.from_url(REDIS_URL)
    with Connection(connection):
        worker = Worker([Queue("backtests")])
        worker.work()


if __name__ == "__main__":
    main()
