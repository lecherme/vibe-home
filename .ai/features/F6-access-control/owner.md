# Access Control — Ownership Boundaries

This is a static ownership map. Runtime state comes from `status.json`.

## Codex

**Owns:**
- `.ai/permissions.md` — role × endpoint permission matrix
- `backend/tests/test_rbac_matrix.py` — comprehensive RBAC integration tests
- `backend/app/api/v1/auth/router.py` — gap fixes only, if required by T02
- `backend/app/api/v1/properties/router.py` — gap fixes only, if required by T02
- `backend/app/api/v1/favorites/router.py` — gap fixes only, if required by T02
- `backend/app/api/v1/admin/router.py` — gap fixes only, if required by T02
- `backend/app/core/security.py` — gap fixes only, if required by T02

**Must NOT:**
- Modify `status.json`
- Create or modify any frontend files
- Modify any file not listed above
- Introduce new endpoints or change existing endpoint signatures

## Gemini

Gemini has no tasks in F6.

## Claude

Claude owns planning, acceptance, and `status.json` updates.

## Boundary Rules

1. Workers must not modify `status.json`.
2. Workers must not create report artifacts directly; wrappers capture stdout.
3. T01 must not modify any backend code — documentation only.
4. T02 may only modify router or security files if a concrete gap was identified in `.ai/permissions.md`.
5. `.ai/permissions.md` is a Claude-visible deliverable file, not an orchestration file; workers may create and read it.
