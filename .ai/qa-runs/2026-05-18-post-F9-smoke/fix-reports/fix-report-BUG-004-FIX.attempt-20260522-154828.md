# Fix Report: BUG-004-FIX

## Ticket Info
- **Review Task:** QA-2026-05-18
- **Affected Task:** Search — BUG-004 — Clear Filters 仅在 no-results 状态显示
- **Criterion:** SRCH-04
- **Files Declared:** frontend/app/(dashboard)/search/page.tsx

## Files Changed
- frontend/app/(dashboard)/search/page.tsx

## Patch Summary
Added `hasActiveFilters` in the search page based on non-empty location or populated `min_price`, `max_price`, `bedrooms`, or `status`. Rendered a `Clear Filters` button below `FilterPanel` and above the results area that calls the existing `handleClearFilters()`, while leaving the no-results `Clear all filters` button unchanged.

## Open Issues
Pre-existing unlisted workspace modifications were present before this fix and were not touched: `.ai/qa-runs/2026-05-18-post-F9-smoke/fix-tickets.md` and `.ai/qa-runs/2026-05-18-post-F9-smoke/status.json`.

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec frontend npx tsc --noEmit` | 无输出 | **PASS — exit 0** |
| 手动复测 SRCH-04 | 待确认 | pending |
