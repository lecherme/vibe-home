# Production Persistence & Deployment — Ownership Boundaries

This is a static ownership map. Runtime state comes from `status.json`.

## Codex

Owns all implementation tasks T01–T05.

**T01 — DB migrations & env vars**
- `backend/migrations/001_create_properties.sql`
- `backend/migrations/002_create_favorites.sql`
- `backend/.env.example`
- `frontend/.env.example`

**T02 — Backend persistence rewrite**
- `backend/app/core/supabase.py`
- `backend/app/data/properties.py`
- `backend/app/services/admin/service.py`
- `backend/app/services/favorites/service.py`
- `backend/app/services/health_service.py`
- `backend/app/api/v1/health.py`
- `backend/requirements.txt`
- `backend/tests/test_health_service.py`
- `backend/tests/test_properties.py`
- `backend/tests/test_admin_properties.py`
- `backend/tests/test_favorites.py`

**T03 — Next.js upgrade**
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/next.config.mjs`
- `frontend/tsconfig.json`

**T04 — Docker & compose**
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `docker-compose.yml`
- `backend/README.md`
- `frontend/README.md`

**T05 — Review**
- `.ai/features/F7-production-persistence-deployment/review.md`

## Gemini

No Gemini tasks in this feature.

## Claude

Claude owns planning, acceptance, and `status.json` updates.

- `.ai/features/F7-production-persistence-deployment/spec.md`
- `.ai/features/F7-production-persistence-deployment/tasks.md`
- `.ai/features/F7-production-persistence-deployment/owner.md`
- `.ai/features/F7-production-persistence-deployment/acceptance.md`
- `.ai/features/F7-production-persistence-deployment/status.json`
- `.ai/features/F7-production-persistence-deployment/final-report.md`

## Boundary Rules

1. Workers must not modify `status.json`.
2. Workers must not create report artifacts directly; wrappers capture stdout.
3. Workers must not modify files outside the current task's declared Scope.
4. If a required change falls outside declared Scope, write a blocker in `## Open Issues` and stop — do not modify the out-of-scope file.
5. Registration-only exemption (≤3 additive lines in a barrel/index/registry file) must be tagged in `## Files Changed`.
