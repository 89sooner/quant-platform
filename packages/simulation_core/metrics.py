"""Core simulation metrics helpers shared by workers and API."""
from __future__ import annotations

from typing import Iterable, List

import numpy as np


def sharpe_ratio(returns: Iterable[float], risk_free_rate: float = 0.0, periods_per_year: int = 365 * 24 * 12) -> float:
    """Compute the Sharpe ratio with a default 5m bar annualisation."""
    series = np.array(list(returns), dtype=float)
    if series.size == 0:
        return 0.0
    excess = series - risk_free_rate
    std = excess.std(ddof=1) if series.size > 1 else 0.0
    if std == 0:
        return 0.0
    return (excess.mean() / std) * np.sqrt(periods_per_year)


def max_drawdown(equity_curve: Iterable[float]) -> float:
    """Return the absolute value of the maximum drawdown."""
    peaks: List[float] = []
    drawdown = 0.0
    for value in equity_curve:
        if not peaks or value > peaks[-1]:
            peaks.append(value)
        current_peak = peaks[-1]
        drawdown = min(drawdown, (value / current_peak) - 1 if current_peak else 0.0)
    return abs(drawdown)
