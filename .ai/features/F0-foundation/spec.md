# F0 — Foundation

## Goal

Establish the minimal two-service skeleton (frontend + backend) with working configuration so every subsequent feature has a consistent, runnable starting point.

## Scope

### Frontend (Next.js)
- Next.js app with App Router initialized
- Tailwind CSS configured
- shadcn/ui initialized (no components installed yet)
- A minimal `/health` status page that fetches `GET /health` from the backend and displays the response
- `.env.example` with required frontend env vars

### Backend (FastAPI)
- FastAPI app with a single `GET /health` endpoint returning `{ "status": "ok" }`
- Supabase connection config loaded from env (no queries yet — config only)
- Folder structure for future features: `api/v1/`, `core/`, `models/`, `schemas/`, `services/`
- `.env.example` with required backend env vars
- `requirements.txt` or `pyproject.toml`

### Repo root
- `README.md` with local setup instructions for both services

## Non-Goals

- No authentication logic
- No database schema or migrations
- No application features (properties, search, favorites, admin)
- No search-service — search is an internal backend module introduced in F3
- No shadcn component installation beyond init
- No deployment configuration

## Constraints

- Frontend is presentational — the health page only displays what the backend returns
- Backend owns all logic — the health endpoint is the only endpoint
- Supabase credentials are placeholder values in `.env.example`; no live connection is required for F0
- No hardcoded URLs or secrets in source
