# Admin Property Management — Tasks

Every task has exactly one owner. Collaboration happens through sequential tasks, not shared tasks.

---

## T01 — Scaffold admin backend schemas and service skeleton

- **owner:** codex
- **type:** scaffold
- **depends_on:** none
- **title:** Scaffold admin Pydantic schemas and service skeleton

**Scope:**
- Create `backend/app/schemas/admin.py` with:
  - `PropertyCreate` schema — all required fields for a new listing (title: str, description: str, price: float, location: str, bedrooms: int, bathrooms: int, area: float, image_url: str = "")
  - `PropertyUpdate` schema — same fields as PropertyCreate but all optional (use Optional)
- Create `backend/app/services/admin/__init__.py`
- Create `backend/app/services/admin/service.py` with:
  - Stub method signatures only: create_property(), update_property(), delete_property()
  - No implementation logic — stubs only

**Allowed file changes:**
- Create: `backend/app/schemas/admin.py`
- Create: `backend/app/services/admin/__init__.py`
- Create: `backend/app/services/admin/service.py`

**Done condition:** All three files exist with correct Pydantic schemas and function stubs; no syntax errors.

---

## T02 — Implement admin endpoints with role enforcement and tests

- **owner:** codex
- **type:** backend
- **depends_on:** T01
- **title:** Implement admin property endpoints with role enforcement and tests

**Scope:**
- Implement full logic in `backend/app/services/admin/service.py`:
  - `create_property(data: PropertyCreate) -> PropertyRead` — add to shared in-memory property store (same store used by F2 endpoints); auto-generate a new unique id; set created_at to current UTC timestamp
  - `update_property(property_id: str, data: PropertyUpdate) -> PropertyRead` — apply partial update to existing property; raise HTTPException 404 if not found
  - `delete_property(property_id: str) -> None` — remove from shared property store; raise HTTPException 404 if not found
- Create `backend/app/api/v1/admin/__init__.py`
- Create `backend/app/api/v1/admin/router.py` with:
  - `POST /api/v1/admin/properties` → 201 PropertyRead; requires admin role; 422 on invalid input
  - `PUT /api/v1/admin/properties/{id}` → 200 PropertyRead; requires admin role; 404 if not found
  - `DELETE /api/v1/admin/properties/{id}` → 204; requires admin role; 404 if not found
  - All endpoints: 401 if not authenticated, 403 if role != admin
- Modify `backend/app/main.py` to include the admin router at `/api/v1/admin`
- Create `backend/tests/test_admin_properties.py` covering:
  - POST creates property and returns 201 with PropertyRead
  - POST returns 422 for missing required fields
  - PUT updates property and returns 200
  - PUT returns 404 for non-existent property
  - DELETE removes property and returns 204
  - DELETE returns 404 for non-existent property
  - After DELETE, property is absent from GET /api/v1/properties list
  - All endpoints return 401 unauthenticated
  - All endpoints return 403 for non-admin (user) role

**Allowed file changes:**
- Modify: `backend/app/services/admin/service.py`
- Create: `backend/app/api/v1/admin/__init__.py`
- Create: `backend/app/api/v1/admin/router.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_admin_properties.py`

**Done condition:** All tests pass; endpoints enforce admin role, return correct status codes, and mutations are reflected in the shared property store.

---

## T03 — Publish frontend types and typed admin API wrapper

- **owner:** codex
- **type:** infra
- **depends_on:** T02
- **title:** Publish frontend types and typed admin API wrapper

**Scope:**
- Create `frontend/types/admin.ts` with:
  - `AdminPropertyCreate` interface matching PropertyCreate backend schema fields
  - `AdminPropertyUpdate` interface — all fields optional (Partial<AdminPropertyCreate>)
- Create `frontend/lib/api/admin.ts` with three functions:
  - `createProperty(data: AdminPropertyCreate): Promise<PropertyRead>` — POST /api/v1/admin/properties
  - `updateProperty(id: string, data: AdminPropertyUpdate): Promise<PropertyRead>` — PUT /api/v1/admin/properties/{id}
  - `deleteProperty(id: string): Promise<void>` — DELETE /api/v1/admin/properties/{id}
- Import `PropertyRead` from `frontend/types/properties.ts` (already exists from F2)
- Ensure all types are exported and usable by the UI layer

**Allowed file changes:**
- Create: `frontend/types/admin.ts`
- Create: `frontend/lib/api/admin.ts`

**Done condition:** TypeScript compiles without errors; three API functions exist with correct signatures; types match backend schemas.

---

## T04 — Implement admin UI

- **owner:** gemini
- **type:** ui
- **depends_on:** T02, T03
- **title:** Implement admin property list, create/edit form, and wire to admin API

**Scope:**
- Create `frontend/components/features/admin/property-form.tsx`:
  - Shared form component for both create and edit
  - Controlled inputs for all PropertyCreate fields (title, description, price, location, bedrooms, bathrooms, area, image_url)
  - Props: `initialValues?: AdminPropertyUpdate`, `onSubmit: (data: AdminPropertyCreate) => Promise<void>`, `isLoading: boolean`
  - Show validation errors inline (required field empty, price must be positive, etc.)
  - Submit button disabled while isLoading
- Create `frontend/app/(dashboard)/admin/properties/page.tsx`:
  - Fetch all properties via existing `propertiesApi.getProperties()` (from F2)
  - Display as table or card list with Edit and Delete action buttons per row
  - Delete button calls `adminApi.deleteProperty(id)` with optimistic removal; shows confirm before calling
  - Edit button links to `/admin/properties/{id}/edit`
  - "Add Property" button links to `/admin/properties/new`
  - Loading skeleton; empty state; error state
- Create `frontend/app/(dashboard)/admin/properties/new/page.tsx`:
  - Renders PropertyForm with empty initialValues
  - On submit: calls `adminApi.createProperty(data)`, redirects to `/admin/properties` on success
  - Shows form-level error if API returns error
- Create `frontend/app/(dashboard)/admin/properties/[id]/edit/page.tsx`:
  - Fetches existing property via `propertiesApi.getProperty(id)` to populate form
  - Renders PropertyForm with existing values as initialValues
  - On submit: calls `adminApi.updateProperty(id, data)`, redirects to `/admin/properties` on success
  - Shows form-level error if API returns error
- Use `lib/api/admin` and `lib/api/properties` only — no direct fetch() or Supabase calls
- All admin pages must be within the `(dashboard)` route group

**Allowed file changes:**
- Create: `frontend/components/features/admin/property-form.tsx`
- Create: `frontend/app/(dashboard)/admin/properties/page.tsx`
- Create: `frontend/app/(dashboard)/admin/properties/new/page.tsx`
- Create: `frontend/app/(dashboard)/admin/properties/[id]/edit/page.tsx`

**Done condition:** Admin property list renders with edit/delete actions; create and edit forms submit correctly; inline validation errors shown; TypeScript compiles clean; loading, empty, and error states present.

---

## T05 — Codex review

- **owner:** codex
- **type:** review
- **depends_on:** T01, T02, T03, T04
- **title:** Review F5-admin-property-management implementation against acceptance criteria

**Scope:**
- Validate all implementation deliverables against `acceptance.md`.
- Check ownership boundaries and task artifacts.
- Verify role enforcement on all admin endpoints (A9, A10).
- Verify deleted properties are absent from property list (A11).
- Verify form validation and inline error display (A17).
- Write `review.md`.

**Done condition:** `review.md` written with a verdict, per-criterion results, and enough failure detail for Claude to choose task_retry, direct_fixup, or review_rerun.

---

## T06 — Claude acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T05
- **title:** Validate F5-admin-property-management and write final acceptance result

**Scope:**
- Read `review.md`.
- Write `final-report.md` with disposition `accepted` or `failed`.
- Update `status.json` feature status to `done` or `failed`.

**Done condition:** `final-report.md` written and `status.json` updated.
