# Problem 1-Pager

## Context
- Build a crypto quant/algo trading platform MVP that supports configuration-driven strategies, backtesting, paper trading, and live trading.
- The codebase is currently empty and must establish a monorepo skeleton spanning frontend (Next.js), API (FastAPI), workers (Freqtrade-based), and infra (docker-compose, migrations).
- Need a structured foundation to iterate quickly while ensuring clarity of responsibilities across services.

## Problem
- Provide the initial scaffolding, configuration, and representative examples that reflect the agreed design so the team can start implementing features without ambiguity.
- Ensure the structure includes strategy DSL, backtest worker codegen, database schema migrations, and environment configuration.

## Goal
- Commit a working repository layout with the described services, example implementations, and documentation for running the platform.
- Include sample FastAPI endpoint, worker job, DSL schema, template, and docker-compose configuration matching the design artifacts shared with the user.

## Non-Goals
- Implement full business logic, data ingestion, or production-ready trading algorithms.
- Deliver exhaustive test coverage or deployment automation beyond docker-compose and initial migrations.

## Constraints
- Follow repository instructions: keep changes safe, avoid secrets, maintain clean structure, ensure files remain within size limits.
- Leverage Freqtrade for backtesting workers and provide integration points without bundling heavy data or credentials.
- Provide at least two implementation options before committing to choices.

## Options Considered
1. **Freqtrade-based workers with FastAPI BFF and Next.js UI (Chosen).**
   - *Pros*: Aligns with shared design, accelerates development using mature backtesting/live trading engine, clear separation of concerns.
   - *Cons*: Adds dependency weight (Freqtrade) and requires Python-specific worker environment.
   - *Risks*: Tight coupling to Freqtrade configuration; future migrations to other engines may require refactoring.
2. **Custom in-house simulation engine and trading core built from scratch.**
   - *Pros*: Full control over implementation details, lighter dependency stack, potentially easier to tailor to unique requirements.
   - *Cons*: Significant engineering effort upfront, higher risk of incorrect simulations, longer path to MVP.
   - *Risks*: Schedule slip, harder to validate accuracy without battle-tested engine.

## Decision
- Proceed with the Freqtrade-based architecture to honor the agreed blueprint and deliver a functional scaffold quickly while documenting extensibility points for future iterations.
