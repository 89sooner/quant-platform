"""Wrapper utilities to orchestrate Freqtrade CLI calls."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, List


def write_freqtrade_config(exchange: str, pairs: List[str], timeframe: str, cash: float) -> Path:
    config = {
        "dry_run": True,
        "exchange": {"name": exchange},
        "stake_currency": "USDT",
        "stake_amount": cash,
        "pair_whitelist": pairs,
        "timeframe": timeframe,
    }
    path = Path("/tmp/freq_config.json")
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


def run_download_data(pairs: List[str], timeframe: str, timerange: str, config_path: Path) -> None:
    command = [
        "freqtrade",
        "download-data",
        "--config",
        str(config_path),
        "--pairs",
        *pairs,
        "--timeframe",
        timeframe,
        "--timerange",
        timerange,
    ]
    subprocess.check_call(command)


def run_backtesting(strategy_class: str, config_path: Path, timerange: str) -> Path:
    output = Path("/tmp") / f"bt_{strategy_class}.json"
    command = [
        "freqtrade",
        "backtesting",
        "--config",
        str(config_path),
        "--strategy",
        strategy_class,
        "--timerange",
        timerange,
        "--export",
        "trades",
        "--export-filename",
        str(output),
    ]
    subprocess.check_call(command)
    return output


def run_backtest_pipeline(payload: Dict) -> Dict[str, str]:
    backtest = payload["backtest"]
    timerange = f"{backtest['start'].replace('-', '')}-{backtest['end'].replace('-', '')}"
    config_path = write_freqtrade_config(payload["exchange"], payload["pairs"], payload["timeframe"], backtest["cash"])
    run_download_data(payload["pairs"], payload["timeframe"], timerange, config_path)
    report_path = run_backtesting(payload["class_name"], config_path, timerange)
    return {"config_path": str(config_path), "report_path": str(report_path)}
