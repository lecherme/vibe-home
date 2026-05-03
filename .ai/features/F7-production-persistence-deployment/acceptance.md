# Production Persistence & Deployment — Acceptance Criteria

T05 (Codex review) verifies every criterion below and writes `review.md`.
T06 (Claude acceptance) reads `review.md` and writes `final-report.md`.

---

## Criteria

| # | Criterion | Check |
|---|-----------|-------|
| A1 | `backend/migrations/001_create_properties.sql` and `002_create_favorites.sql` exist with correct DDL; `favorites` has UNIQUE(user_id, property_id) | Read migration files; verify column definitions and constraints |
| A2 | Property reads/writes (`backend/app/data/properties.py`), favorites reads/writes (`backend/app/services/favorites/service.py`), and admin CRUD (`backend/app/services/admin/service.py`) all go through the Supabase client; no in-memory stores remain | Grep for in-memory list/dict stores in those three files; verify Supabase client calls |
| A3 | All five Supabase env vars present in `backend/.env.example` and `frontend/.env.example` | Read both `.env.example` files |
| A4 | `GET /health` returns non-200 when Supabase connectivity check fails | Read health service + router implementation |
| A5 | `pytest backend/tests/` exits 0 | Run pytest and confirm exit code |
| A6 | `npm audit --audit-level=high` inside `frontend/` exits 0 after Next.js upgrade | Run npm audit and confirm exit code |
| A7 | `backend/Dockerfile`, `frontend/Dockerfile`, and `docker-compose.yml` exist; `docker compose up` starts both services and the stack is functional without manual post-start steps | Verify files exist; confirm compose references both services; verify health endpoint reachable |
| A8 | `backend/README.md` and `frontend/README.md` contain env var tables covering all new Supabase vars | Read README files |

---

## Review and Acceptance

If review verdict is FAIL, Claude does NOT proceed directly to T06 acceptance.
Claude must:
1. Write `last_review_failure` to `status.json` with `fix_path`, `failed_criteria`, and `fix_instructions`.
2. Choose fix_path: `task_retry`, `direct_fixup`, or `review_rerun`.
3. Apply the fix and re-run review before acceptance.

## Rejection Conditions

- Any task modifies files outside its declared Scope in `tasks.md`.
- Any worker modifies `status.json`.
- Any required artifact is missing or malformed.
- In-memory data stores remain in any of the three service files after T02.
