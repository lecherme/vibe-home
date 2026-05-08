# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | `backend/migrations/001_create_properties.sql` and `002_create_favorites.sql` exist. `favorites` includes `UNIQUE (user_id, property_id)`. |
| A2 | FAIL | Runtime code still contains in-memory persistence paths: `FakeSupabaseClient` fallback in `backend/app/core/supabase.py`, seeded `_PROPERTY_SEED`/`PROPERTIES` in `backend/app/data/properties.py`, and `favorites_store` proxy in `backend/app/services/favorites/service.py`. |
| A3 | PASS | `backend/.env.example` and `frontend/.env.example` contain the required Supabase variables. |
| A4 | FAIL | `/health` returns `503` only when a query throws, but `get_supabase_client()` silently falls back to an in-memory fake client when `SUPABASE_SERVICE_ROLE_KEY` is missing or the library is unavailable, so broken Supabase configuration can still report healthy. |
| A5 | FAIL | `python3 -m pytest backend/tests/` cannot run in this sandbox (`No module named pytest`). Independently of that, the persistence tests still set `SUPABASE_KEY` and manipulate `PROPERTIES` / `favorites_store`, so they are not validating the new `SUPABASE_SERVICE_ROLE_KEY` path. |
| A6 | PASS | `frontend/package.json` is upgraded to `next@^16.2.4`. The T03 artifact reports `npm audit --audit-level=high` passed locally on Node `20.20.2`; I could not rerun it here because npm registry access is blocked. |
| A7 | FAIL | `backend/Dockerfile`, `frontend/Dockerfile`, and `docker-compose.yml` exist, and `docker compose config` is valid. End-to-end `docker compose up --build` was not completed in the task artifact and could not be reproduced here due Docker daemon denial; the false-positive health fallback also undermines stack validation. |
| A8 | PASS | `backend/README.md` and `frontend/README.md` include env var tables covering the new Supabase variables. |

## Issues Found
- BLOCKER: `backend/app/core/supabase.py:170-203`, `backend/app/data/properties.py:13-335`, and `backend/app/services/favorites/service.py:11-29` preserve in-memory fallback storage. That violates the requirement to replace all in-memory stores with Supabase-backed persistence.
- BLOCKER: `backend/app/services/health_service.py:5-11` relies on `get_supabase_client()`, but `backend/app/core/supabase.py:174-190` returns a fake client when real Supabase setup is missing. `/health` can return 200 for a misconfigured deployment.
- BLOCKER: `backend/tests/test_properties.py:18-21`, `backend/tests/test_admin_properties.py:21-30`, and `backend/tests/test_favorites.py:25-32` still configure only `SUPABASE_KEY` and reset `PROPERTIES` / `favorites_store`. The tests are wired to the fallback store, not the new persistence layer.
- BLOCKER: `frontend/next-env.d.ts:1-6` was modified even though T03 scope allowed only `frontend/package.json`, `frontend/package-lock.json`, `frontend/next.config.mjs`, and `frontend/tsconfig.json`. That is a boundary violation under the feature rejection rules.
- WARNING: `docker compose up --build` is still unverified end-to-end. The T04 artifact already documents that gap, and local reproduction here is blocked by Docker permissions.
- MINOR: `frontend/types/favorites.ts:3-7` defines camelCase fields (`propertyId`, `userId`, `createdAt`), while the backend response type is snake_case in `backend/app/schemas/favorite.py:5-8`. The API type exists, but it does not match the actual contract.

## Required Fixes
- Remove the fake Supabase fallback and in-memory seed/proxy path from runtime persistence code. Runtime reads/writes and health checks must fail against broken Supabase configuration instead of silently using local memory.
- Update backend persistence tests to target the real Supabase client contract or explicit client mocks for that contract, using `SUPABASE_SERVICE_ROLE_KEY` rather than the legacy-only setup.
- Make `/health` return non-200 for missing/invalid Supabase configuration as well as query failures, then rerun the backend health tests.
- Revert the out-of-scope `frontend/next-env.d.ts` change or formally re-scope the task before re-review.
- Re-run end-to-end Docker validation after the persistence and health fixes and capture a successful `docker compose up --build` result.

## Approved Items
- SQL migration files are present and the favorites uniqueness constraint is correctly defined.
- Required Supabase env vars are documented in both `.env.example` files and both READMEs.
- Frontend upgrade artifacts for Next.js are present, and the dependency bump matches the stated security goal.
- Dockerfiles are multi-stage and use `uvicorn` / `next start` in the final stage as required.
- No feature business logic was moved into frontend components; the frontend feature changes are limited to config, Docker, and documentation.
- `status.json` shows only `by: "claude"` activity entries, and I found no evidence in the task artifacts that Codex or Gemini modified it.
