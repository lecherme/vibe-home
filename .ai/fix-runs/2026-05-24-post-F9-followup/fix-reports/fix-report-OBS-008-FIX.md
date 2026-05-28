# Fix Report: OBS-008-FIX

## Ticket Info
- **Review Task:** open-bugs.md
- **Affected Task:** Search — OBS-008 — Bathroom 筛选缺失
- **Criterion:** OBS-008
- **Files Declared:** backend/app/schemas/search.py, backend/app/api/v1/properties/router.py, backend/app/services/search/service.py, frontend/types/search.ts, frontend/lib/api/properties.ts, frontend/app/(dashboard)/search/page.tsx, frontend/components/features/search/filter-panel.tsx

## Files Changed
- backend/app/schemas/search.py
- backend/app/api/v1/properties/router.py
- backend/app/services/search/service.py
- frontend/types/search.ts
- frontend/lib/api/properties.ts
- frontend/app/(dashboard)/search/page.tsx
- frontend/components/features/search/filter-panel.tsx

## Patch Summary
Added `bathrooms` to the backend search filter schema, router query params, and service filtering with N+ bathroom matching. Added frontend bathroom filter typing, query serialization, URL state sync, active-filter detection, and a Min Bathrooms select in the search filter panel.

## Open Issues
None.

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec frontend npx tsc --noEmit` | 无输出 | **PASS — exit 0** |
| `docker compose exec backend python -c "from app.services.search.service import search"` | 无输出 | **PASS — exit 0** |
| 手动复测 | Min Bathrooms select 显示（Any / 1+ baths … 5+ baths）；筛选生效，结果只显示 ≥ N 间浴室房源；URL `?bathrooms=N` 正确写入；Clear Filters 清空；back/forward 还原；bedrooms + bathrooms 组合筛选正常 | **PASS — 2026-05-28** |
