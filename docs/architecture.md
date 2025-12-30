# TrackMyBets 2.0 Architecture

## Problem statement
Sportsbet punters can export their entire account transactions history as CSV. Today that data is difficult to interpret and rarely highlights net losses. TrackMyBets 2.0 ingests those CSV files, normalises the data, calculates profit/loss by several dimensions, and renders interactive visualisations that show how often a user loses money compared to their perceived performance.

## MVP scope
- Upload one or more Sportsbet CSV exports (drag-and-drop) and treat subsequent uploads as incremental refreshes.
- Parse bets, deposits, withdrawals, and bonus bets while reconciling stake, payout, commission, and settlement timestamps.
- Persist normalised data so that users can revisit dashboards without re-uploading.
- Provide dashboards/tables for:
  - Profit & loss over time (daily/weekly/monthly roll-ups)
  - Breakdown by sport, competition/league, teams/participants, market type, and bet type (single vs multi)
  - Highlight of best/worst bets and biggest bankroll swings
- Provide contextual copy explaining Sportsbet bet types (linked to help-centre docs).

## Target users & personas
1. **Recreational bettor** – uploads history occasionally to see total losses vs deposits.
2. **Responsible gambling coach** – uses anonymised exports to illustrate patterns to clients.
3. **Data-minded punter** – wants to drill into sports/teams where they lose most.

## System overview
```
┌────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│ Sportsbet  │ CSV │  Upload/API  │     │ Processing  │     │   Database    │
│ CSV export ├────▶│ (FastAPI)    ├────▶│  (Pandas +  ├────▶│ (DuckDB/     │
└────────────┘     │  S3/local)   │     │ SQLAlchemy) │     │  SQLite)     │
                                          │                │
                                          ▼                │
                                     ┌────────────┐        │
                                     │ Aggregates │◀───────┘
                                     └────────────┘
                                             │ REST/WS
                                             ▼
                                       ┌────────────┐
                                       │ React/Vite │
                                       │ dashboards │
                                       └────────────┘
```

### Key components
- **Frontend (React + Vite + TypeScript)** – Handles CSV uploads, shows progress, stores auth tokens, visualises analytics with Recharts/VisX, orchestrates filters.
- **Backend API (FastAPI)** – Receives uploads (multipart or presigned URL), validates CSV schema, pushes file to `data/ingest/`, triggers parsing pipeline, serves aggregated analytics endpoints, and returns metadata for progress updates.
- **Processing layer** – Pandas/Polars transforms to map Sportsbet columns to canonical schema, compute derived measures (implied probability, return on investment), and feed them into relational tables via SQLAlchemy. Use Pydantic models for validation + shared schema output.
- **Persistence** – SQLite or DuckDB for local-first dev; abstracts behind repository to swap to Postgres later. Tables: `users`, `uploads`, `bets`, `legs`, `transactions`, materialized views for `bet_metrics` and `time_series`.
- **Static knowledge base** – JSON definitions for bet types scraped/manual summarised from Sportsbet help centre.
- **Sportsbet helper extension** – Browser exporter that sits in its own repository (`../tmb-activity-downloader`). Users download the ZIP from `frontend/public/trackmybets-helper-extension.zip`, which is rebuilt from the external repo whenever the extension changes.

## Data lifecycle
1. **Upload**: CSV sent to `/api/uploads` → entry created in `uploads` table (status `received`). Large files optionally chunked to object storage (S3 compatible) but MVP can store locally under `data/raw/<upload_id>.csv`.
2. **Validation**: Async task ensures column headers, encodings, and duplicates match expectations. Invalid rows logged + surfaced to user.
3. **Normalization**: Parser converts currencies to decimal, identifies sports/competitions/teams, classifies bet types, splits multi-bets into legs.
4. **Persistence**: Upsert semantics keyed by Sportsbet `Transaction ID` to support re-upload / incremental refresh without duplication. Upload status moves to `processed`.
5. **Analytics**: Materialized views refreshed after each upload; metrics exposed through `/api/metrics/{dimension}` endpoints with query params `from`, `to`, `sport`, `team`, etc.
6. **Visualization**: Frontend fetches aggregated slices and renders charts. Filters send query params and results cached client-side.

## Technology choices
- **Language**: Python 3.11 for backend due to mature CSV + data tools; TypeScript for frontend.
- **Backend stack**: FastAPI, Uvicorn, Pydantic, SQLAlchemy 2.0, Pandas or Polars (configurable), Arrow/DuckDB for analytical joins, Celery/RQ (optional) for async processing.
- **Frontend stack**: Vite, React 18, TanStack Router/Query, Tailwind CSS for rapid styling, Recharts or Nivo for visualisations.
- **State management**: Query caching (TanStack Query) + lightweight Zustand store for filters.
- **Auth**: MVP uses device-local session (no multi-user). Future: email magic-link via Supabase/Auth0.
- **Testing**: Pytest + HTTPX for backend; Vitest + React Testing Library for frontend; contract tests in `shared/` using open-source `typia` or `pydantic` schema exports.

## Deployment
- MVP can run entirely on a single Docker Compose stack (FastAPI + SQLite + Vite dev server behind Nginx). Later, plan for managed Postgres, object storage, and container-based deployment.

## Folder structure rationale
```
TrackMyBets 2.0/
├── backend/
│   ├── app/
│   │   ├── api/            # routers (uploads, metrics, reference data)
│   │   ├── core/           # settings, logging, dependencies
│   │   ├── models/         # SQLAlchemy models + Pydantic schemas
│   │   ├── services/       # ingestion, analytics and betting domain logic
│   │   ├── workers/        # async jobs (Celery/RQ) for parsing large files
│   │   └── main.py         # FastAPI app entrypoint
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── features/
│   │   │   ├── upload/
│   │   │   ├── dashboard/
│   │   │   └── knowledge-base/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── main.tsx
│   ├── public/
│   └── package.json
├── shared/
│   ├── schemas/       # Auto-generated OpenAPI/TypeScript bindings later
│   └── README.md
├── docs/
│   └── architecture.md
└── .env.example
```

## Data model sketch
- `users`: (id, device_hash, created_at)
- `uploads`: (id, user_id, filename, status, row_count, processed_at)
- `transactions`: (id, sportsbet_id, upload_id, type, amount, currency, occurred_at)
- `bets`: (id, transaction_id, bet_type, sport, competition, description, stake, payout, status)
- `bet_legs`: (id, bet_id, team, opponent, market, odds, result)
- `metrics_daily`: (date, user_id, stake, payout, profit, roi)
- `metrics_dimension`: (dimension_key, dimension_value, metric_name, metric_value)

## Incremental upload strategy
- Use `sportsbet_transaction_id` as unique key.
- When processing a new CSV, upsert each row; if duplicates exist, keep the one with the latest `LastUpdateDate` (if available) or `upload_id` ordering.
- Keep `uploads` table as audit log with counts of inserted/updated rows for user feedback.

## Error handling & observability
- Structured logging (pydantic settings + loguru) with ingestion job IDs.
- Store rejected rows in `data/rejects/<upload_id>.csv` for debugging.
- Surface ingestion progress via `/api/uploads/{id}`.

## Privacy & security considerations
- All files stored locally/on device for MVP; emphasise that nothing leaves the machine.
- Provide ability to delete all data (drop DB + raw files) through CLI command.
- Mask personally identifiable information when rendering charts unless needed.

## Backlog highlights
1. **MVP**
   - CSV upload endpoint + parsing pipeline
   - Persist bets + metrics, basic dashboards
   - Downloadable PDF/CSV summary
2. **Short-term**
   - Compare periods (YoY, MoM)
   - Benchmark vs average punter stats
   - Responsible gambling tips overlay
3. **Long-term**
   - Multi-device sync (Supabase/Postgres)
   - Real-time odds ingestion from APIs
   - Notification engine for betting limits
