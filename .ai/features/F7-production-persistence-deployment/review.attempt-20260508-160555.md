# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | [`backend/migrations/001_create_properties.sql:1`](/Users/xiangzhifeng/Desktop/code/vibe_home/backend/migrations/001_create_properties.sql:1) defines `properties` with the expected columns and constraints. [`backend/migrations/002_create_favorites.sql:1`](/Users/xiangzhifeng/Desktop/code/vibe_home/backend/migrations/002_create_favorites.sql:1) defines `favorites` with `UNIQUE (user_id, property_id)`. |
| A2 | PASS | Property reads in [`backend/app/data/properties.py:11`](/Users/xiangzhifeng/Desktop/code/vibe_home/backend/app/data/properties.py:11), admin CRUD in [`backend/app/services/admin/service.py:17`](/Users/xiangzhifeng/Desktop/code/vibe_home/backend/app/services/admin/service.py:17), and favorites reads/writes in [`backend/app/services/favorites/service.py:12`](/Users/xiangzhifeng/Desktop/code/vibe_home/backend/app/services/favorites/service.py:12) all go through `get_supabase_client().table(...)`. I found no remaining in-memory store in those task-owned runtime files. |
| A3 | PASS | [`backend/.env.example:1`](/Users/xiangzhifeng/Desktop/code/vibe_home/backend/.env.example:1) includes `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `SUPABASE_ANON_KEY`. [`frontend/.env.example:1`](/Users/xiangzhifeng/Desktop/code/vibe_home/frontend/.env.example:1) includes `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`. |
| A4 | PASS | [`backend/app/services/health_service.py:5`](/Users/xiangzhifeng/Desktop/code/vibe_home/backend/app/services/health_service.py:5) returns `status="error"` on Supabase init/query failure, and [`backend/app/api/v1/health.py:10`](/Users/xiangzhifeng/Desktop/code/vibe_home/backend/app/api/v1/health.py:10) maps that to HTTP 503. |
| A5 | FAIL | `python3 -m pytest backend/tests/` does not run in this sandbox (`No module named pytest`), and there is no recorded successful full-suite run in [`codex-build-T02.md:1`](/Users/xiangzhifeng/Desktop/code/vibe_home/.ai/features/F7-production-persistence-deployment/codex-build-T02.md:1) even though [`tasks.md:42`](/Users/xiangzhifeng/Desktop/code/vibe_home/.ai/features/F7-production-persistence-deployment/tasks.md:42) and [`acceptance.md:16`](/Users/xiangzhifeng/Desktop/code/vibe_home/.ai/features/F7-production-persistence-deployment/acceptance.md:16) require it. |
| A6 | PASS | [`frontend/package.json`](/Users/xiangzhifeng/Desktop/code/vibe_home/frontend/package.json:1) upgrades `next` to `^16.2.4`. [`codex-build-T03.md:19`](/Users/xiangzhifeng/Desktop/code/vibe_home/.ai/features/F7-production-persistence-deployment/codex-build-T03.md:19) records a user-verified clean `npm audit --audit-level=high` and successful build on Node `20.20.2`. |
| A7 | PASS | [`backend/Dockerfile`](/Users/xiangzhifeng/Desktop/code/vibe_home/backend/Dockerfile:1), [`frontend/Dockerfile`](/Users/xiangzhifeng/Desktop/code/vibe_home/frontend/Dockerfile:1), and [`docker-compose.yml:1`](/Users/xiangzhifeng/Desktop/code/vibe_home/docker-compose.yml:1) exist and wire both services together. [`status.json:415`](/Users/xiangzhifeng/Desktop/code/vibe_home/.ai/features/F7-production-persistence-deployment/status.json:415) records human verification on 2026-05-08 that `docker compose up --build` succeeded and `GET /health` returned HTTP 200. |
| A8 | PASS | [`backend/README.md:9`](/Users/xiangzhifeng/Desktop/code/vibe_home/backend/README.md:9) and [`frontend/README.md:9`](/Users/xiangzhifeng/Desktop/code/vibe_home/frontend/README.md:9) contain env var tables covering the Supabase vars. |

## Issues Found
- BLOCKER: T03 modified [`frontend/next-env.d.ts:1`](/Users/xiangzhifeng/Desktop/code/vibe_home/frontend/next-env.d.ts:1), but T03 scope is limited to [`tasks.md:52`](/Users/xiangzhifeng/Desktop/code/vibe_home/.ai/features/F7-production-persistence-deployment/tasks.md:52) and [`owner.md:28`](/Users/xiangzhifeng/Desktop/code/vibe_home/.ai/features/F7-production-persistence-deployment/owner.md:28). This is an explicit boundary violation.
- BLOCKER: T02 also touched out-of-scope files: [`backend/app/services/favorites/__init__.py:1`](/Users/xiangzhifeng/Desktop/code/vibe_home/backend/app/services/favorites/__init__.py:1) is not in T02 scope per [`owner.md:15`](/Users/xiangzhifeng/Desktop/code/vibe_home/.ai/features/F7-production-persistence-deployment/owner.md:15), and the fix-loop change to [`backend/tests/test_rbac_matrix.py:1`](/Users/xiangzhifeng/Desktop/code/vibe_home/backend/tests/test_rbac_matrix.py:1) is likewise outside the declared file list. [`status.json:160`](/Users/xiangzhifeng/Desktop/code/vibe_home/.ai/features/F7-production-persistence-deployment/status.json:160) and [`fix-report-fix-A5-test-rbac.md:3`](/Users/xiangzhifeng/Desktop/code/vibe_home/.ai/features/F7-production-persistence-deployment/fix-reports/fix-report-fix-A5-test-rbac.md:3) tie those edits to this feature work.
- BLOCKER: A5 is not satisfied. The required command cannot be run here, and the canonical T02 artifact [`codex-build-T02.md:1`](/Users/xiangzhifeng/Desktop/code/vibe_home/.ai/features/F7-production-persistence-deployment/codex-build-T02.md:1) does not document a successful `pytest backend/tests/` run.
- WARNING: A6 and A7 depend on recorded local/human verification rather than reproducible sandbox runs: [`codex-build-T03.md:19`](/Users/xiangzhifeng/Desktop/code/vibe_home/.ai/features/F7-production-persistence-deployment/codex-build-T03.md:19) and [`status.json:415`](/Users/xiangzhifeng/Desktop/code/vibe_home/.ai/features/F7-production-persistence-deployment/status.json:415).
- MINOR: [`frontend/types/favorites.ts:3`](/Users/xiangzhifeng/Desktop/code/vibe_home/frontend/types/favorites.ts:3) uses camelCase fields while [`backend/app/schemas/favorite.py:5`](/Users/xiangzhifeng/Desktop/code/vibe_home/backend/app/schemas/favorite.py:5) is snake_case.

## Required Fixes
- Remove or formally re-scope the out-of-scope T03 change to `frontend/next-env.d.ts` before acceptance.
- Remove or formally re-scope the out-of-scope T02 changes to `backend/app/services/favorites/__init__.py` and `backend/tests/test_rbac_matrix.py` before acceptance.
- Execute `pytest backend/tests/` in a real backend environment with dependencies installed, capture a successful exit, and update the T02 evidence so A5 is actually proven.

## Approved Items
- Supabase migration files are present and correctly define `properties` and `favorites`.
- Runtime persistence for properties, favorites, and admin CRUD is now Supabase-backed in the task-owned service files.
- `/health` now fails closed when Supabase init or connectivity fails.
- Required Supabase env vars are documented in both `.env.example` files and both READMEs.
- Frontend API types are published under `frontend/types/`.
- I found no feature business logic moved into frontend components; network/auth logic remains in `frontend/lib/api/*` and `frontend/lib/auth/*`.
- I found no `"by": "codex"` or `"by": "gemini"` activity entries in `status.json`.
