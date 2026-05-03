# Production Persistence & Deployment — Tasks

Every task has exactly one owner. Collaboration happens through sequential tasks, not shared tasks.

---

## T01 — DB migrations & env vars

- **owner:** codex
- **type:** scaffold
- **depends_on:** none

**Scope:**
- `backend/migrations/001_create_properties.sql` — CREATE TABLE for `properties` mirroring existing schema
- `backend/migrations/002_create_favorites.sql` — CREATE TABLE for `favorites` with UNIQUE(user_id, property_id)
- `backend/.env.example` — add `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`
- `frontend/.env.example` — add `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`

**Done condition:** Both SQL migration files exist with correct DDL; both `.env.example` files contain the five Supabase vars. Artifact: `codex-build-T01.md`.

---

## T02 — Backend persistence rewrite

- **owner:** codex
- **type:** build
- **depends_on:** T01

**Scope:**
- `backend/app/core/supabase.py` — Supabase client singleton (SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY)
- `backend/app/data/properties.py` — replace in-memory list with Supabase-backed reads/writes
- `backend/app/services/admin/service.py` — rewrite create/update/delete to persist to Supabase `properties` table
- `backend/app/services/favorites/service.py` — rewrite to persist to Supabase `favorites` table
- `backend/app/services/health_service.py` — add Supabase connectivity check; return error status if unreachable
- `backend/app/api/v1/health.py` — propagate non-200 when Supabase unreachable
- `backend/requirements.txt` — add `supabase` client library if not already present
- `backend/tests/test_health_service.py` — update to cover Supabase-reachable and Supabase-unreachable paths
- `backend/tests/test_properties.py` — update fixtures/mocks for Supabase-backed property reads
- `backend/tests/test_admin_properties.py` — update fixtures/mocks for Supabase-backed admin CRUD
- `backend/tests/test_favorites.py` — update fixtures/mocks for Supabase-backed favorites reads/writes

**Done condition:** All services read/write via Supabase client; `pytest backend/tests/` exits 0; health endpoint returns non-200 when Supabase connectivity check fails. Artifact: `codex-build-T02.md`.

---

## T03 — Next.js upgrade

- **owner:** codex
- **type:** build
- **depends_on:** T01

**Scope:**
- `frontend/package.json` — bump `next` to a version with no open high/critical CVEs
- `frontend/package-lock.json` — updated by npm install
- `frontend/next.config.mjs` — fix breaking-change config syntax if required by the new version
- `frontend/tsconfig.json` — fix breaking-change TypeScript compiler options if required by the new version

**Done condition:** `npm audit --audit-level=high` inside `frontend/` exits 0; `npm run build` succeeds. Artifact: `codex-build-T03.md`.

---

## T04 — Docker & compose

- **owner:** codex
- **type:** build
- **depends_on:** T02, T03

**Scope:**
- `backend/Dockerfile` — multi-stage production image for FastAPI; final stage CMD runs uvicorn
- `frontend/Dockerfile` — multi-stage production image for Next.js; final stage CMD runs next start
- `docker-compose.yml` — at repo root; orchestrates backend + frontend with correct env var pass-through
- `backend/README.md` — add env var table for all Supabase vars
- `frontend/README.md` — add env var table for all Supabase vars

**Done condition:** Running `docker compose up` (with env vars supplied via `.env` files) starts both services without errors and the stack is functional — backend health endpoint returns 200, frontend serves the app; no manual post-start steps required. Artifact: `codex-build-T04.md`.

---

## T05 — Codex review

- **owner:** codex
- **type:** review
- **depends_on:** T02, T03, T04

**Scope:**
- Validate all deliverables against `acceptance.md` criteria A1–A8.
- Check ownership boundaries and file scope per task.
- Write `review.md`.

**Done condition:** `review.md` written with verdict (PASS/FAIL), per-criterion results A1–A8, and enough failure detail for Claude to choose `task_retry`, `direct_fixup`, or `review_rerun`.

---

## T06 — Claude acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T05

**Scope:**
- Read `review.md`.
- Write `final-report.md` with disposition `accepted` or `failed`.
- Update `status.json` feature status to `done` or `failed`.

**Done condition:** `final-report.md` written and `status.json` updated.
