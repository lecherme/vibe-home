# Admin Property Management — Acceptance Criteria

T05 (Codex review) verifies every criterion below and writes `review.md`.
T06 (Claude acceptance) reads `review.md` and writes `final-report.md`.

---

## Criteria

| # | Criterion | Check |
|---|-----------|-------|
| A1 | PropertyCreate and PropertyUpdate Pydantic schemas exist in backend/app/schemas/admin.py | File exists check |
| A2 | AdminService implements create_property(), update_property(), delete_property() | Backend code review |
| A3 | POST /api/v1/admin/properties creates listing and returns 201 with PropertyRead | Backend test |
| A4 | POST /api/v1/admin/properties returns 422 for missing required fields | Backend test |
| A5 | PUT /api/v1/admin/properties/{id} updates listing and returns 200 with PropertyRead | Backend test |
| A6 | PUT /api/v1/admin/properties/{id} returns 404 for non-existent property | Backend test |
| A7 | DELETE /api/v1/admin/properties/{id} removes listing and returns 204 | Backend test |
| A8 | DELETE /api/v1/admin/properties/{id} returns 404 for non-existent property | Backend test |
| A9 | All admin endpoints return 401 for unauthenticated requests | Backend test |
| A10 | All admin endpoints return 403 for non-admin role (user role) | Backend test |
| A11 | Deleted properties no longer appear in GET /api/v1/properties list | Backend test |
| A12 | frontend/types/admin.ts exists with AdminPropertyCreate and AdminPropertyUpdate interfaces | File exists check |
| A13 | frontend/lib/api/admin.ts exists with createProperty(), updateProperty(), deleteProperty() | File exists check |
| A14 | Admin property list page exists at frontend/app/(dashboard)/admin/properties/page.tsx | File exists check |
| A15 | Property create page exists at frontend/app/(dashboard)/admin/properties/new/page.tsx | File exists check |
| A16 | Property edit page exists at frontend/app/(dashboard)/admin/properties/[id]/edit/page.tsx | File exists check |
| A17 | PropertyForm shows validation errors inline (required field empty, invalid price) | Frontend code review |
| A18 | Admin UI uses only lib/api/admin and lib/api/properties — no direct fetch() or Supabase calls | Frontend code review |
| A19 | All backend tests in test_admin_properties.py pass | Test execution |
| A20 | Frontend TypeScript compiles without errors | Build check |

## Review and Acceptance

If review verdict is FAIL, Claude does NOT proceed directly to T06 acceptance.
Claude must:
1. Write `last_review_failure` to `status.json` with fix_path, failed_criteria, and fix_instructions.
2. Choose fix_path: task_retry, direct_fixup, or review_rerun.
3. Apply the fix and re-run review before acceptance.

## Rejection Conditions

- Any task modifies files outside its ownership boundary.
- Any worker modifies `status.json`.
- Any required artifact is missing or malformed.
- Non-admin users can access admin endpoints (A10 failed).
- Deleted properties still appear in property list (A11 failed).
- Admin service operates on a separate store instead of the shared F2 property store.
