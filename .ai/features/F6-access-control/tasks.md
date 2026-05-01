# Access Control — Tasks

Every task has exactly one owner. F6 has no UI tasks and no Gemini tasks.

---

## T01 — Document permission matrix

- **owner:** codex
- **type:** infra
- **depends_on:** none
- **title:** Audit all endpoints and produce permission matrix

**Scope:**
- Read all four routers: `backend/app/api/v1/auth/router.py`, `backend/app/api/v1/properties/router.py`, `backend/app/api/v1/favorites/router.py`, `backend/app/api/v1/admin/router.py`
- Create `.ai/permissions.md` with a table covering all 11 endpoints × {unauthenticated, user, admin}
- For each cell, document: expected HTTP status code and the guard mechanism (e.g. `get_current_user`, `require_role("admin")`, inline role check)
- Identify any RBAC gaps — endpoints that do not enforce the role behaviour defined in `spec.md`
- Do NOT fix gaps in this task — document them only

**Allowed file changes:**
- Create: `.ai/permissions.md`

**Done condition:** `.ai/permissions.md` exists; table covers all 11 endpoints × 3 auth states; any identified gaps are listed.

---

## T02 — Write RBAC integration tests and fix gaps

- **owner:** codex
- **type:** backend
- **depends_on:** T01
- **title:** Write comprehensive role × endpoint integration tests and fix any RBAC gaps

**Scope:**
- Create `backend/tests/test_rbac_matrix.py` with parametrized tests covering every endpoint × {unauthenticated, user, admin}
  - At minimum 33 test cases (11 endpoints × 3 states)
  - Each case asserts the exact expected HTTP status code from the matrix in `.ai/permissions.md`
- Fix any gaps identified in T01 by modifying the relevant router or security helper
  - Only modify files listed in allowed_files below
  - Preserve all existing behaviour for already-correct cases
- Re-run existing backend test suite to confirm no regressions

**Allowed file changes:**
- Create: `backend/tests/test_rbac_matrix.py`
- Modify (only if a gap requires it): `backend/app/api/v1/auth/router.py`
- Modify (only if a gap requires it): `backend/app/api/v1/properties/router.py`
- Modify (only if a gap requires it): `backend/app/api/v1/favorites/router.py`
- Modify (only if a gap requires it): `backend/app/api/v1/admin/router.py`
- Modify (only if a gap requires it): `backend/app/core/security.py`

**Done condition:** `test_rbac_matrix.py` covers all 11 × 3 cases; all tests pass; full backend suite passes without regressions.

---

## T03 — Codex review

- **owner:** codex
- **type:** review
- **depends_on:** T01, T02
- **title:** Review F6-access-control implementation against acceptance criteria

**Scope:**
- Validate `.ai/permissions.md` against `acceptance.md` criteria
- Validate `test_rbac_matrix.py` coverage and pass results
- Verify no endpoint returns 200 for a denied role
- Write `review.md`

**Done condition:** `review.md` written with a verdict, per-criterion results, and enough failure detail for Claude to choose task_retry, direct_fixup, or review_rerun.

---

## T04 — Claude acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T03
- **title:** Validate F6-access-control and write final acceptance result

**Scope:**
- Read `review.md`
- Write `final-report.md` with disposition `accepted` or `failed`
- Update `status.json` feature status to `done` or `failed`

**Done condition:** `final-report.md` written and `status.json` updated.
