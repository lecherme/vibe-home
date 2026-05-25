# Fix Report: BUG-011-FIX

## Ticket Info
- **Review Task:** open-bugs.md
- **Affected Task:** Admin — BUG-011 — Admin 房源列表无分页
- **Criterion:** BUG-011
- **Files Declared:** frontend/app/(dashboard)/admin/properties/page.tsx

## Files Changed
- frontend/app/(dashboard)/admin/properties/page.tsx

## Patch Summary
Added admin property pagination state with `PAGE_SIZE = 20`, updated fetching to call `propertiesApi.list(page, PAGE_SIZE)` and store `total`. Added Previous/Next controls below the table and adjusted delete refresh behavior to move back one page when deleting the only item on a non-first page.

## Open Issues
None

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec frontend npx tsc --noEmit` | 无输出 | **PASS — exit 0** |
| 手动复测 BUG-011 | 待确认 | pending |
