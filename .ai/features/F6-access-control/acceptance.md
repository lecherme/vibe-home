# Access Control — Acceptance Criteria

T03 (Codex review) verifies every criterion below and writes `review.md`.
T04 (Claude acceptance) reads `review.md` and writes `final-report.md`.

---

## Criteria

| # | Criterion | Check |
|---|-----------|-------|
| A1 | `.ai/permissions.md` exists | File exists check |
| A2 | Matrix covers all 11 endpoints × {unauthenticated, user, admin} with expected status codes | Document review |
| A3 | `backend/tests/test_rbac_matrix.py` exists | File exists check |
| A4 | Tests cover all 11 endpoints × 3 auth states (minimum 33 parametrized cases) | Code review |
| A5 | All tests in `test_rbac_matrix.py` pass | Test execution |
| A6 | GET /api/v1/auth/me returns 401 unauthenticated, 200 for user, 200 for admin | Test |
| A7 | GET /api/v1/properties (list, search, detail) returns 401 unauthenticated, 200 for user, 200 for admin | Test |
| A8 | POST/DELETE/GET /api/v1/favorites/* returns 401 unauthenticated, 200/201/204 for user, 403 for admin | Test |
| A9 | POST/PUT/DELETE /api/v1/admin/properties/* returns 401 unauthenticated, 403 for user, 200/201/204 for admin | Test |
| A10 | Full backend test suite passes without regressions after any gap fixes | Test execution |

## Review and Acceptance

If review verdict is FAIL, Claude does NOT proceed directly to T04 acceptance.
Claude must:
1. Write `last_review_failure` to `status.json` with fix_path, failed_criteria, and fix_instructions.
2. Choose fix_path: task_retry, direct_fixup, or review_rerun.
3. Apply the fix and re-run review before acceptance.

## Rejection Conditions

- `.ai/permissions.md` is missing or does not cover all 11 endpoints.
- Any test case is missing from the 11 × 3 matrix.
- Any endpoint returns 200 for a role that should be denied (A8 or A9 failed).
- Full backend suite has regressions after gap fixes (A10 failed).
- Any worker modifies `status.json`.
