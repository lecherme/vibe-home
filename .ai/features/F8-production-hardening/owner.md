# Production Hardening — Ownership Boundaries

This is a static ownership map. Runtime state comes from `status.json`.

## Codex

Owns all implementation tasks T01–T05.

**T01 — CORS hardening**
- `backend/app/main.py`
- `backend/.env.example`

**T02 — Auth rate limiting**
- `backend/requirements.txt`
- `backend/app/main.py`
- `backend/app/api/v1/auth/router.py`
- `backend/.env.example`
- `backend/tests/test_rate_limiting.py`

**T03 — Structured JSON logging**
- `backend/app/main.py`
- `backend/app/core/logging.py` (if extracted)

**T04 — Cascade delete favorites**
- `backend/app/services/admin/service.py`
- `backend/tests/test_admin_properties.py`

**T05 — Review**
- `.ai/features/F8-production-hardening/review.md`

## Gemini

No Gemini tasks in this feature.

## Claude

Claude owns planning, acceptance, and `status.json` updates.

- `.ai/features/F8-production-hardening/spec.md`
- `.ai/features/F8-production-hardening/tasks.md`
- `.ai/features/F8-production-hardening/owner.md`
- `.ai/features/F8-production-hardening/acceptance.md`
- `.ai/features/F8-production-hardening/status.json`
- `.ai/features/F8-production-hardening/final-report.md`

## Boundary Rules

1. Workers must not modify `status.json`.
2. Workers must not create report artifacts directly; wrappers capture stdout.
3. Workers must not modify files outside the current task's declared Scope.
4. If a required change falls outside declared Scope, write a blocker in `## Open Issues` and stop — do not modify the out-of-scope file.
5. Registration-only exemption (≤3 additive lines in a barrel/index/registry file) must be tagged in `## Files Changed`.
