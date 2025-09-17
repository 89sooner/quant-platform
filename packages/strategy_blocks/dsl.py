"""Strategy DSL definitions shared across services."""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, validator


class Block(BaseModel):
    """Single strategy building block used by the DSL."""

    id: str
    type: Literal["EMA", "SMA", "RSI", "ATR", "CrossOver", "Rule"]
    params: Optional[Dict[str, Any]] = None
    inputs: Optional[List[str]] = None
    expr: Optional[str] = None

    @validator("id")
    def _validate_id(cls, value: str) -> str:  # noqa: N805 - pydantic validator signature
        if not value:
            raise ValueError("block id cannot be empty")
        return value


class StrategyDSL(BaseModel):
    """Top-level DSL payload."""

    blocks: List[Block]
    risk: Dict[str, Any] = Field(default_factory=dict)
    execution: Dict[str, Any] = Field(default_factory=dict)

    @validator("blocks")
    def _unique_ids(cls, value: List[Block]) -> List[Block]:  # noqa: N805
        ids = [block.id for block in value]
        if len(ids) != len(set(ids)):
            raise ValueError("block ids must be unique")
        return value
