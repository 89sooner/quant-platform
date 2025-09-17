"""Seed script for inserting sample exchanges and symbols."""
from __future__ import annotations

import os
from dataclasses import dataclass

import psycopg2


@dataclass
class SymbolSeed:
    exchange: str
    symbol: str
    base: str
    quote: str


SEEDS = [
    SymbolSeed("binance", "BTC/USDT", "BTC", "USDT"),
    SymbolSeed("binance", "ETH/USDT", "ETH", "USDT"),
]


def seed_database() -> None:
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        dbname=os.getenv("POSTGRES_DB", "quant"),
        user=os.getenv("POSTGRES_USER", "quant"),
        password=os.getenv("POSTGRES_PASSWORD", "quantpw"),
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("INSERT INTO exchanges (name, code) VALUES (%s, %s) ON CONFLICT (code) DO NOTHING", ("Binance", "binance"))
        for seed in SEEDS:
            cur.execute(
                """
                INSERT INTO symbols (exchange_id, symbol, base, quote)
                SELECT id, %s, %s, %s FROM exchanges WHERE code = %s
                ON CONFLICT (exchange_id, symbol) DO NOTHING
                """,
                (seed.symbol, seed.base, seed.quote, seed.exchange),
            )
    conn.close()


if __name__ == "__main__":
    seed_database()
