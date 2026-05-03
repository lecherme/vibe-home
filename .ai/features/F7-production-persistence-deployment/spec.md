# Production Persistence & Deployment

## Goal

Replace all in-memory data stores with Supabase-backed persistence so that property and favorites data survive backend restarts. Upgrade Next.js to a version free of high/critical CVEs. Provide Dockerfiles and a `docker-compose.yml` so the complete stack can be run locally or deployed without manual steps.

## Scope

### Backend
- Supabase `properties` table: schema and SQL migration file
- Supabase `favorites` table: schema and SQL migration file; unique constraint on `(user_id, property_id)`
- `PropertyService` and `FavoritesService` rewritten to use Supabase client (replacing all in-memory stores)
- Admin create/update/delete endpoints persisted to Supabase
- `GET /health` updated to verify Supabase connectivity (returns non-200 if unreachable)
- All existing backend tests pass against the new persistence layer

### Frontend
- Next.js upgraded to a version with no open high/critical CVEs (`npm audit` clean)
- Any breaking-change compatibility issues resolved (e.g. `next.config.js` syntax, deprecated APIs)

### Infrastructure
- `backend/Dockerfile` — multi-stage production image for FastAPI; runs with `uvicorn`
- `frontend/Dockerfile` — multi-stage production image for Next.js; runs with `next start`
- `docker-compose.yml` at repo root — orchestrates backend and frontend; `docker compose up` requires no manual steps
- Backend and frontend `.env.example` and `README.md` updated with all new env vars

## Non-Goals

- Seed / mock data population after migration
- Image upload (placeholder URLs continue)
- Multi-region or CDN configuration
- New user-facing features or UI changes
- Search service extraction (deferred to F9)

## Constraints

- All implementation must follow `.ai/conventions.md` and `.ai/orchestration.md`.
- Workers must implement only their assigned task.
- `status.json` is updated only by Claude Code orchestration.
- No hardcoded URLs, keys, or secrets in any source file.
- Backend must use the Supabase client library for data access (not raw psycopg2 or hand-rolled HTTP unless via migration SQL files).

## Dependencies

- F6 (Access Control) — must be `done`

## Required Env Vars

### Backend (new or confirmed)
- `SUPABASE_URL` — Supabase project REST URL
- `SUPABASE_SERVICE_ROLE_KEY` — service role key for backend reads/writes
- `SUPABASE_ANON_KEY` — anon key (already present from F0/F1; confirm documented)

### Frontend (new or confirmed)
- `NEXT_PUBLIC_SUPABASE_URL` — same Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` — anon key

All vars must appear in `backend/.env.example`, `frontend/.env.example`, and the env var section of each service's `README.md`.
