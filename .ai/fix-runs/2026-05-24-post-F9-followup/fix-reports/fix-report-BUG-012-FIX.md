# Fix Report: BUG-012-FIX

## Ticket Info
- **Review Task:** open-bugs.md
- **Affected Task:** Admin — BUG-012 — Admin 表单 image_url 与 Property.images 不一致
- **Criterion:** BUG-012
- **Files Declared:** backend/app/schemas/admin.py, backend/app/services/admin/service.py, frontend/types/admin.ts, frontend/components/features/admin/property-form.tsx, frontend/app/(dashboard)/admin/properties/[id]/edit/page.tsx

## Files Changed
- backend/app/schemas/admin.py
- backend/app/services/admin/service.py
- frontend/types/admin.ts
- frontend/components/features/admin/property-form.tsx
- frontend/app/(dashboard)/admin/properties/[id]/edit/page.tsx

## Patch Summary
Replaced admin `image_url` (single string) with `images: list[str]` across backend schemas and service. Removed `_build_images()` adapter. Frontend type and form updated: dynamic URL list (max 5, Add/Remove buttons, Remove disabled when only 1 entry, empty strings filtered on submit). Edit page maps `property.images ?? []`. Remove button `disabled` alignment patched via Claude-authorized fallback (2026-05-26).

## Open Issues
None.

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec frontend npx tsc --noEmit` | 无输出 | **PASS — exit 0** |
| `docker compose exec backend python -c "from app.services.admin.service import create_property"` | 无输出 | **PASS — exit 0** |
| 手动复测 BUG-012 | 新增多图、编辑保留多图、Remove disabled 全 PASS | **PASS — 2026-05-26** |
