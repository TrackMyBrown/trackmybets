# TrackMyBets 2.0 Frontend

## Getting started
1. Install dependencies with `pnpm install` (preferred) or `npm install` inside `frontend/`.
2. Copy `.env.example` from repo root to `frontend/.env` (or rely on Vite `import.meta.env`).
3. Run `pnpm dev` to start the Vite dev server at http://localhost:5173.

## Architecture highlights
- React + TypeScript app bootstrapped with Vite.
- Feature-based directory structure under `src/features` for upload flow, dashboards, and educational content.
- QueryClient from TanStack Query will power data fetching + caching once backend endpoints are ready.
- Zustand store will hold global filters/feature flags (to be added).

## Next steps
- Implement API hooks for `/api/uploads/csv` and `/api/metrics/*` endpoints.
- Replace placeholder cards in `MetricsOverview` with live data and charts (Recharts/Nivo).
- Introduce router (TanStack Router) for multi-view navigation (overview, sport breakdown, team leaderboard, etc.).
