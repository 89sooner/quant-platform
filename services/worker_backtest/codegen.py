"""Generate Freqtrade strategy classes from the strategy DSL."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader

from packages.strategy_blocks.dsl import Block, StrategyDSL

TEMPLATES = Path(__file__).parent / "templates"


def _sanitize(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", name)


def _build_indicator_lines(blocks: List[Block]) -> List[str]:
    lines: List[str] = []
    for block in blocks:
        params = block.params or {}
        if block.type == "EMA":
            period = int(params.get("period", 12))
            lines.append(f"df['{block.id}'] = ta.EMA(df, timeperiod={period})")
        elif block.type == "SMA":
            period = int(params.get("period", 20))
            lines.append(f"df['{block.id}'] = ta.SMA(df, timeperiod={period})")
        elif block.type == "RSI":
            period = int(params.get("period", 14))
            lines.append(f"df['{block.id}'] = ta.RSI(df, timeperiod={period})")
        elif block.type == "ATR":
            period = int(params.get("period", 14))
            lines.append(f"df['{block.id}'] = ta.ATR(df, timeperiod={period})")
        elif block.type == "CrossOver":
            a, b = (block.inputs or ["a", "b"])[:2]
            lines.append(
                f"df['{block.id}_up'] = (df['{a}'] > df['{b}']) & (df['{a}'].shift(1) <= df['{b}'].shift(1))"
            )
            lines.append(
                f"df['{block.id}_down'] = (df['{a}'] < df['{b}']) & (df['{a}'].shift(1) >= df['{b}'].shift(1))"
            )
        elif block.type == "Rule":
            continue
        else:
            raise ValueError(f"Unsupported block type: {block.type}")
    return lines


def _expr_to_pandas(expr: str) -> str:
    parsed = re.sub(
        r"cross\.([A-Za-z0-9_]+)\.(up|down)",
        lambda match: f"df['{match.group(1)}_{match.group(2)}']",
        expr,
    )
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", parsed)
    for token in sorted(set(tokens), key=len, reverse=True):
        if token in {"and", "or", "not", "True", "False"}:
            continue
        parsed = re.sub(rf"\b{token}\b", f"df['{token}']", parsed)
    return (
        parsed.replace(" and ", " & ")
        .replace(" or ", " | ")
        .replace(" not ", " ~ ")
    )


def render_strategy(dsl_payload: Dict, class_name: str, timeframe: str, can_short: bool = False) -> str:
    model = StrategyDSL(**dsl_payload)
    indicator_lines = _build_indicator_lines(model.blocks)
    entry_long = entry_short = exit_long = exit_short = None

    for block in model.blocks:
        if block.type != "Rule" or not block.expr:
            continue
        text = block.expr.strip()
        if text.startswith("long:"):
            entry_long = _expr_to_pandas(text.split(":", 1)[1])
        elif text.startswith("short:"):
            entry_short = _expr_to_pandas(text.split(":", 1)[1])
        elif text.startswith("exit_long:"):
            exit_long = _expr_to_pandas(text.split(":", 1)[1])
        elif text.startswith("exit_short:"):
            exit_short = _expr_to_pandas(text.split(":", 1)[1])

    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template("freqtrade_strategy.j2")
    return template.render(
        class_name=_sanitize(class_name),
        timeframe=timeframe,
        can_short=can_short,
        indicator_lines=indicator_lines,
        entry_long=entry_long,
        entry_short=entry_short,
        exit_long=exit_long,
        exit_short=exit_short,
    )


def write_strategy_file(code: str, output_dir: Path, class_name: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"{class_name}.py"
    target.write_text(code, encoding="utf-8")
    return target
