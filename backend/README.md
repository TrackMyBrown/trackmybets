# TrackMyBets 2.0 Backend

## Getting started
1. Install uv or poetry (recommended: `pip install uv`).
2. From `backend/`, run `uv sync --extra dev` to create a virtual environment and install dependencies.
3. Copy `.env.example` to `.env` at repo root and adjust directories.
4. Initialise the database schema once with `uv run python -m app.cli init-db`.
5. Launch the API with `uv run fastapi dev app/main.py --reload` (or `uvicorn app.main:app --reload`).

## Next steps
- Flesh out `app/api/uploads.py` to persist raw CSV files and enqueue parsing jobs.
- Implement domain models under `app/models` and migrations via Alembic.
- Add services in `app/services` for ingestion + analytics rollups.
- Fill out `backend/tests/` with Pytest suites covering CSV parsing and metrics endpoints.
