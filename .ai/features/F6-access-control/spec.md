# Access Control

## Goal

Audit and harden all backend endpoints to ensure RBAC is consistently enforced across every feature (F1–F5). Define and publish a machine-readable permission matrix. Write a comprehensive integration test suite covering every endpoint × role combination. Fix any gaps found during the audit.

## Scope

**Backend — Codex:**
- Audit all 11 endpoints across four routers: auth, properties, favorites, admin
- Produce `.ai/permissions.md` with the complete role × endpoint permission matrix
- Write `backend/tests/test_rbac_matrix.py` covering every endpoint × {unauthenticated, user, admin}
- Fix any endpoint that does not enforce the correct role behaviour

**No UI changes.** This feature touches backend and test files only.

## Endpoints in scope

| Router | Endpoint |
|--------|----------|
| auth | GET /api/v1/auth/me |
| properties | GET /api/v1/properties |
| properties | GET /api/v1/properties/search |
| properties | GET /api/v1/properties/{id} |
| favorites | POST /api/v1/favorites/{property_id} |
| favorites | DELETE /api/v1/favorites/{property_id} |
| favorites | GET /api/v1/favorites |
| favorites | GET /api/v1/favorites/{property_id} |
| admin | POST /api/v1/admin/properties |
| admin | PUT /api/v1/admin/properties/{id} |
| admin | DELETE /api/v1/admin/properties/{id} |

## Expected role behaviour

| Endpoint group | unauthenticated | user | admin |
|----------------|-----------------|------|-------|
| GET /auth/me | 401 | 200 | 200 |
| GET /properties (list, search, detail) | 401 | 200 | 200 |
| POST/DELETE/GET /favorites/* | 401 | 200/201/204 | 403 |
| POST/PUT/DELETE /admin/properties/* | 401 | 403 | 200/201/204 |

## Non-Goals

- New user-facing features
- UI changes
- Fine-grained per-resource permissions (row-level security is Supabase-managed)
- Buyer/agent role distinction (deferred — current codebase only requires user and admin)

## Constraints

- Workers must implement only their assigned task.
- `status.json` is updated only by Claude Code orchestration.
- `.ai/permissions.md` is a deliverable artifact owned by Codex (T01), not a runtime file.

## Dependencies

- F1-authentication-roles (done)
- F2-property-browsing (done)
- F3-search-filtering (done)
- F4-favorites (done)
- F5-admin-property-management (done)

## Required Env Vars

No new env vars.
