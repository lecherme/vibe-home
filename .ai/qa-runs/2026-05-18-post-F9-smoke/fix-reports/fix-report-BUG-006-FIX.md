# Fix Report: BUG-006-FIX

## Ticket Info
- **Review Task:** QA-2026-05-18
- **Affected Task:** AdminCRUD — 后端 admin role claim mismatch — security.py reads wrong JWT path
- **Criterion:** ADMIN-03
- **Files Declared:** backend/app/core/security.py

## Files Changed
- backend/app/core/security.py

## Patch Summary
Replaced `payload.get("app_role")` in `get_current_user()` with a fallback that also reads `payload.get("app_metadata", {}).get("app_role")`, preserving support for the existing top-level claim.

## Open Issues
`pytest` could not be run because `pytest` is not installed for `python3` in this environment; `python3 -m py_compile backend/app/core/security.py` passed. Pre-existing unlisted worktree changes were present in `.ai/qa-runs/2026-05-18-post-F9-smoke/fix-tickets.md` and `.ai/qa-runs/2026-05-18-post-F9-smoke/status.json`; they were not touched.

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec backend pytest or equivalent, exit 0` | `============================= test session starts ==============================` | **FAIL** |
