# TrackMyBets 2.0

TrackMyBets 2.0 is a web-based visual analytics tool that helps punters understand betting activity and profit/loss using CSV exports from Sportsbet. This repository contains the architecture proposal and a starter scaffold for the MVP described in the accompanying documents.

## High-level objectives
- Accept Sportsbet CSV exports through a secure upload workflow.
- Parse, normalize, and persist transactions to power longitudinal analysis across multiple uploads.
- Surface interactive dashboards that highlight profit/loss by sport, competition, team, bet type, and time period.
- Educate users by contextualising each bet type using Sportsbet's help-centre descriptions.

## Repository layout
- `docs/architecture.md` – end-to-end architecture, data flow, and backlog for the MVP.
- `backend/` – FastAPI service skeleton (ingestion API, data model, persistence, aggregation jobs).
- `frontend/` – Vite + React + TypeScript client scaffold for uploads, dashboards, and shared components.
- `shared/` – placeholder for cross-stack schemas (Pydantic/TypeScript) that will be generated later.
- `data/` (to be created at runtime) – stanza for local CSV/SQLite/DuckDB artifacts ignored by git.
- **Helper extension lives in a separate repo** (`../tmb-activity-downloader`). See below for packaging instructions.

## Next steps
1. Finalise dependencies (see backend `pyproject.toml` and frontend `package.json`) and bootstrap the dev environment.
2. Implement CSV parsing + persistence, then wire ingestion endpoints. (Initial upload persistence scaffolding is now in place.)
3. Build upload UI + overview dashboard, iterating on the visual grammar defined in the architecture notes. (Vite/React shell now fetches `/metrics/overview`.)
4. Add tests (unit + contract) and analytics seed data to de-risk production ingest.

## Running locally
1. **Backend**
   ```bash
   cd backend
   uv sync --extra dev  # or poetry/pip install -r
   uv run python -m app.cli init-db  # one-time schema init
   uv run fastapi dev app/main.py --reload
   ```
2. **Frontend**
   ```bash
   cd frontend
   pnpm install  # or npm install
   pnpm dev
   ```
3. Visit http://localhost:5173 to upload a CSV; API requests default to http://127.0.0.1:8000.

Refer to `docs/architecture.md` for detailed module breakdowns, data lifecycle, and backlog.

## Browser extension (separate repository)
The Sportsbet downloader extension now lives outside this mono-repo so it can be versioned and distributed independently:

- Source: `/Users/adamk/Documents/Scripting/tmb-activity-downloader` (or clone from the corresponding GitHub repo).
- Build/update ZIP for the frontend download with the helper script in this repo:
  ```bash
  cd "/Users/adamk/Documents/Scripting/TrackMyBets 2.0"
  ./scripts/build-extension.sh
  ```
  Set `TRACKMYBETS_EXTENSION_DIR` if the extension lives somewhere else.
- The frontend serves `frontend/public/trackmybets-helper-extension.zip` so users can download the helper directly; rerun the script above whenever the extension changes.
