# Admin Property Management

## Goal

Admin users can create, edit, and delete property listings through a dedicated admin interface. All admin operations are protected by role enforcement — only users with `role=admin` may access these endpoints or pages.

## Scope

**Backend (Codex):**
- `PropertyCreate` and `PropertyUpdate` Pydantic schemas for admin write operations
- `POST /api/v1/admin/properties` — create listing; returns 201 with PropertyRead on success, 422 on missing/invalid fields
- `PUT /api/v1/admin/properties/{id}` — update listing; returns 200 with PropertyRead on success, 404 if not found, 422 on invalid fields
- `DELETE /api/v1/admin/properties/{id}` — delete listing; returns 204 on success, 404 if not found
- All admin endpoints enforce `role=admin`: 401 for unauthenticated, 403 for non-admin role
- Deleted properties must not appear in `GET /api/v1/properties` (shared in-memory store)

**Frontend — Codex:**
- `frontend/types/admin.ts` — AdminPropertyCreate and AdminPropertyUpdate TypeScript interfaces
- `frontend/lib/api/admin.ts` — createProperty(), updateProperty(), deleteProperty() typed wrappers

**Frontend — Gemini:**
- `frontend/app/(dashboard)/admin/properties/page.tsx` — admin property list with edit/delete actions
- `frontend/app/(dashboard)/admin/properties/new/page.tsx` — create property page
- `frontend/app/(dashboard)/admin/properties/[id]/edit/page.tsx` — edit property page
- `frontend/components/features/admin/property-form.tsx` — shared create/edit form component with inline validation errors

## Non-Goals

- Bulk import / CSV upload
- Image upload (placeholder image URL field is sufficient)
- Audit log / change history
- Draft / publish workflow

## Constraints

- All implementation must follow `.ai/conventions.md` and `.ai/orchestration.md`.
- Workers must implement only their assigned task.
- `status.json` is updated only by Claude Code orchestration.
- Admin endpoints live under `/api/v1/admin/` — not mixed into the public properties router.

## Dependencies

- F1-authentication-roles (done) — JWT middleware and role guard required
- F2-property-browsing (done) — shared in-memory property store required

## Required Env Vars

No new env vars.
