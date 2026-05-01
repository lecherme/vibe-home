# Admin Property Management — Ownership Boundaries

This is a static ownership map. Runtime state comes from `status.json`.

## Codex

**Owns:**
- `backend/app/schemas/admin.py` — PropertyCreate, PropertyUpdate Pydantic schemas
- `backend/app/services/admin/__init__.py` — service package init
- `backend/app/services/admin/service.py` — admin service implementation
- `backend/app/api/v1/admin/__init__.py` — router package init
- `backend/app/api/v1/admin/router.py` — POST, PUT, DELETE admin property endpoints
- `backend/app/main.py` — router registration only (minimal change)
- `backend/tests/test_admin_properties.py` — admin endpoint tests
- `frontend/types/admin.ts` — AdminPropertyCreate, AdminPropertyUpdate TypeScript interfaces
- `frontend/lib/api/admin.ts` — createProperty(), updateProperty(), deleteProperty() wrappers

**Must NOT:**
- Create or modify UI components or pages
- Modify shadcn primitives in `components/ui/`
- Modify frontend files outside `types/` and `lib/api/`
- Modify the public properties router or service (use the shared store reference only)

## Gemini

**Owns:**
- `frontend/components/features/admin/property-form.tsx` — shared create/edit form component
- `frontend/app/(dashboard)/admin/properties/page.tsx` — admin property list page
- `frontend/app/(dashboard)/admin/properties/new/page.tsx` — create property page
- `frontend/app/(dashboard)/admin/properties/[id]/edit/page.tsx` — edit property page

**Must NOT:**
- Modify `backend/` directory
- Modify `frontend/lib/api/` or `frontend/types/`
- Implement business logic in components
- Call Supabase directly
- Create new API endpoints or schemas

## Claude

Claude owns planning, acceptance, and `status.json` updates.

## Boundary Rules

1. Workers must not modify `status.json`.
2. Workers must not create report artifacts directly; wrappers capture stdout.
3. Workers must not modify files outside the current task scope.
4. Admin endpoints must live in a dedicated `/api/v1/admin/` router, not merged into the public properties router.
5. All admin pages must be under the `(dashboard)` route group.
6. Non-admin role (user) must be denied 403 on all admin endpoints.
7. The admin service must operate on the same shared in-memory property store introduced in F2, not a separate store.
