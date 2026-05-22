# Fix Report: BUG-004-FIX

## Ticket Info
- **Review Task:** QA-2026-05-18
- **Affected Task:** Search — BUG-004 — Clear Filters 仅在 no-results 状态显示
- **Criterion:** SRCH-04
- **Files Declared:** frontend/app/(dashboard)/search/page.tsx

## Files Changed
- frontend/app/(dashboard)/search/page.tsx

## Patch Summary
Moved the `Clear Filters` button into the SearchBar row, with `SearchBar` wrapped in `flex-1` and the button rendered immediately after it. Removed the first-version `hasActiveFilters` placement below `FilterPanel`; the no-results `Clear all filters` button was left unchanged.

## Open Issues
Pre-existing unlisted dirty worktree entries were present in `.ai/qa-runs/2026-05-18-post-F9-smoke/...`, including `status.json` and a fix report file. I did not modify those files.

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec frontend npx tsc --noEmit` | 无输出 | **PASS — exit 0** |
| 手动复测 SRCH-04 | 全部验收点通过（2026-05-22） | **PASS** |
