# Fix Report: BUG-010-FIX

## Ticket Info
- **Review Task:** open-bugs.md
- **Affected Task:** Favorites — BUG-010 — Favorites 分页缺失 + ghost unfavorited
- **Criterion:** BUG-010
- **Files Declared:** frontend/app/(dashboard)/favorites/page.tsx, frontend/lib/api/favorites.ts, frontend/app/(dashboard)/search/page.tsx

## Files Changed
- frontend/lib/api/favorites.ts
- frontend/app/(dashboard)/search/page.tsx
- frontend/app/(dashboard)/favorites/page.tsx

## Patch Summary
Added `getAllFavoriteIds()` to page through favorites in batches of 50 and return a full `Set` of property ids. Replaced search’s fixed `getFavorites(1, 100)` lookup with the new helper and silent empty-set fallback. Added URL-backed favorites pagination, total tracking, paged loading, pagination controls, and refresh/page-back behavior after unfavorite.

## Open Issues
None.

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec frontend npx tsc --noEmit` | 无输出 | **PASS — exit 0** |
| 手动复测 BUG-010 | /favorites 分页、URL params、取消收藏边界；/search 收藏同步回归全 PASS | **PASS — 2026-05-26** |
