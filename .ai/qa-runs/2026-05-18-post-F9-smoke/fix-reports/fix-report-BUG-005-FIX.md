# Fix Report: BUG-005-FIX

## Ticket Info
- **Review Task:** QA-2026-05-18
- **Affected Task:** AdminAccess — Admin role claim mismatch — middleware reads wrong JWT path
- **Criterion:** ADMIN-01
- **Files Declared:** frontend/middleware.ts

## Files Changed
- frontend/middleware.ts

## Patch Summary
Updated `JwtPayload` in `frontend/middleware.ts` to include `app_metadata?: { app_role?: AppRole }`. Replaced the admin role lookup so it checks the top-level `app_role` claim first, then falls back to `app_metadata.app_role`.

## Open Issues
Pre-existing unlisted worktree changes were present before this patch in `.ai/qa-runs/...`; they were not modified by this fix.

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `npx tsc --noEmit in frontend directory, exit 0; then manual retest ADMIN-01` | `bash: -c: line 1: syntax error near unexpected token `then'` | **FAIL** |
