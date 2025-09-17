# Quant Platform Monorepo

This repository hosts the MVP scaffold for a crypto quantitative trading platform. It follows the architecture discussed with the product stakeholder: a Next.js web UI, FastAPI backend-for-frontend, Freqtrade-powered workers, and shared Python packages.

## Getting Started

1. Copy `.env.sample` to `.env` and adjust secrets.
2. Run the infrastructure stack:
   ```bash
   docker compose -f infra/docker-compose.yml up -d --build
   ```
3. Apply database migrations:
   ```bash
   docker compose -f infra/docker-compose.yml exec api alembic upgrade head
   ```
4. Access services:
   - Web UI: http://localhost:3000
   - API docs: http://localhost:8000/docs
   - MinIO console: http://localhost:9001

## Repository Layout

```
quant-platform/
├─ apps/
│  ├─ web/                 # Next.js (app router)
│  └─ api/                 # FastAPI BFF
├─ services/
│  ├─ worker_backtest/     # Freqtrade-based backtest worker
│  ├─ worker_live/         # Live/paper trading worker scaffold
│  └─ ingestor/            # Market data ingestion service scaffold
├─ packages/
│  ├─ strategy_blocks/     # Shared strategy DSL definitions
│  └─ simulation_core/     # Shared simulation models/utilities
├─ infra/
│  ├─ docker-compose.yml   # Local stack
│  └─ migrations/          # Alembic migrations
├─ scripts/                # Utilities (e.g., seeding)
└─ docs/                   # Planning artifacts
```

## Development Notes

- Workers rely on Freqtrade, Redis (RQ), and Postgres/TimescaleDB.
- The FastAPI BFF enqueues jobs for workers and exposes strategy/backtest endpoints.
- Strategy code is generated from DSL blocks and rendered through Jinja templates before being executed by Freqtrade.

Refer to `docs/plan/problem-1-pager.md` for context, goals, and decision rationale.
