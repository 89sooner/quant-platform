"""Initial schema for quant platform."""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20250916_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")

    op.create_table(
        "exchanges",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("code", sa.Text, nullable=False, unique=True),
    )

    op.create_table(
        "symbols",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("exchange_id", sa.Integer, sa.ForeignKey("exchanges.id")),
        sa.Column("symbol", sa.Text, nullable=False),
        sa.Column("base", sa.Text, nullable=False),
        sa.Column("quote", sa.Text, nullable=False),
        sa.Column("min_notional", sa.Numeric),
        sa.Column("lot_step", sa.Numeric),
        sa.Column("price_step", sa.Numeric),
        sa.UniqueConstraint("exchange_id", "symbol", name="uq_symbols_exchange_symbol"),
    )

    op.create_table(
        "candles",
        sa.Column("exchange_id", sa.Integer),
        sa.Column("symbol_id", sa.Integer),
        sa.Column("timeframe", sa.Text),
        sa.Column("ts", sa.TIMESTAMP(timezone=True)),
        sa.Column("open", sa.Numeric),
        sa.Column("high", sa.Numeric),
        sa.Column("low", sa.Numeric),
        sa.Column("close", sa.Numeric),
        sa.Column("volume", sa.Numeric),
        sa.PrimaryKeyConstraint("exchange_id", "symbol_id", "timeframe", "ts", name="pk_candles"),
    )
    op.execute("SELECT create_hypertable('candles', by_range('ts'), if_not_exists => TRUE);")

    op.create_table(
        "funding",
        sa.Column("exchange_id", sa.Integer),
        sa.Column("symbol_id", sa.Integer),
        sa.Column("ts", sa.TIMESTAMP(timezone=True)),
        sa.Column("rate", sa.Numeric),
        sa.PrimaryKeyConstraint("exchange_id", "symbol_id", "ts", name="pk_funding"),
    )
    op.execute("SELECT create_hypertable('funding', by_range('ts'), if_not_exists => TRUE);")

    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.create_table(
        "strategies",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "strategy_versions",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("strategy_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("strategies.id")),
        sa.Column("schema_json", sa.JSON, nullable=False),
        sa.Column("code_ref", sa.Text),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "bots",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("strategy_version_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("strategy_versions.id")),
        sa.Column("mode", sa.Text),
        sa.Column("exchange_id", sa.Integer, sa.ForeignKey("exchanges.id")),
        sa.Column("symbols", sa.ARRAY(sa.Text), nullable=False),
        sa.Column("params", sa.JSON, nullable=False),
        sa.Column("risk", sa.JSON, nullable=False),
        sa.Column("execution", sa.JSON, nullable=False),
        sa.Column("status", sa.Text, server_default="idle"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "runs_backtest",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("bot_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("bots.id")),
        sa.Column("period", sa.dialects.postgresql.TSRANGE, nullable=False),
        sa.Column("cash", sa.Numeric, nullable=False),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.Column("finished_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("result_json", sa.JSON),
        sa.Column("artifact_uri", sa.Text),
    )

    op.create_table(
        "run_trades",
        sa.Column("run_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("runs_backtest.id")),
        sa.Column("ts_open", sa.TIMESTAMP(timezone=True)),
        sa.Column("ts_close", sa.TIMESTAMP(timezone=True)),
        sa.Column("side", sa.Text),
        sa.Column("entry", sa.Numeric),
        sa.Column("exit", sa.Numeric),
        sa.Column("qty", sa.Numeric),
        sa.Column("pnl", sa.Numeric),
        sa.Column("fee", sa.Numeric),
        sa.Column("mae", sa.Numeric),
        sa.Column("mfe", sa.Numeric),
        sa.PrimaryKeyConstraint("run_id", "ts_open", "ts_close", name="pk_run_trades"),
    )

    op.create_table(
        "run_metrics",
        sa.Column("run_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("runs_backtest.id"), primary_key=True),
        sa.Column("cagr", sa.Numeric),
        sa.Column("sharpe", sa.Numeric),
        sa.Column("sortino", sa.Numeric),
        sa.Column("calmar", sa.Numeric),
        sa.Column("mdd", sa.Numeric),
        sa.Column("winrate", sa.Numeric),
        sa.Column("pf", sa.Numeric),
        sa.Column("trades", sa.Integer),
        sa.Column("exposure", sa.Numeric),
        sa.Column("avg_r", sa.Numeric),
        sa.Column("dd_recovery_days", sa.Integer),
    )

    op.create_table(
        "live_positions",
        sa.Column("bot_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("bots.id")),
        sa.Column("symbol", sa.Text),
        sa.Column("side", sa.Text),
        sa.Column("qty", sa.Numeric),
        sa.Column("avg_price", sa.Numeric),
        sa.Column("unrealized_pnl", sa.Numeric),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("bot_id", "symbol", name="pk_live_positions"),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("bot_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("bots.id")),
        sa.Column("level", sa.Text),
        sa.Column("message", sa.Text),
        sa.Column("meta", sa.JSON),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    for table in [
        "alerts",
        "live_positions",
        "run_metrics",
        "run_trades",
        "runs_backtest",
        "bots",
        "strategy_versions",
        "strategies",
        "funding",
        "candles",
        "symbols",
        "exchanges",
    ]:
        op.drop_table(table)
