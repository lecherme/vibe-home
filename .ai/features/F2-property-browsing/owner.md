# F2 — Ownership Boundaries

## Codex

Codex owns all backend code and all frontend infrastructure (library and type layers).

| Path | Scope |
|------|-------|
| `backend/app/schemas/property.py` | `Property`, `PropertyStatus`, `PropertyListResponse` Pydantic schemas |
| `backend/app/data/properties.py` | In-memory seed store and accessor functions |
| `backend/app/api/v1/properties/` | Property router and endpoints |
| `backend/app/main.py` | Register properties router (additive change only) |
| `backend/tests/test_properties.py` | Property endpoint unit tests |
| `frontend/lib/api/properties.ts` | `propertiesApi.list` and `propertiesApi.get` typed wrappers |
| `frontend/types/property.ts` | `Property`, `PropertyStatus`, `PropertyListResponse` TypeScript types |

Codex must NOT touch:
- `frontend/app/` (Gemini owns pages)
- `frontend/components/` (Gemini owns UI components)
- Any F1 files already in `frontend/lib/auth/`, `frontend/lib/api/auth.ts`,
  `frontend/middleware.ts`, `frontend/types/auth.ts` (already done — do not modify)

---

## Gemini

Gemini owns all frontend UI: pages and feature components.

| Path | Scope |
|------|-------|
| `frontend/app/(dashboard)/layout.tsx` | Authenticated shell layout with nav bar |
| `frontend/app/(dashboard)/properties/page.tsx` | Property list page |
| `frontend/app/(dashboard)/properties/[id]/page.tsx` | Property detail page |
| `frontend/components/features/properties/PropertyCard.tsx` | Property card component |
| `frontend/components/features/properties/PropertyDetail.tsx` | Property detail component |
| `frontend/components/features/properties/PropertyListSkeleton.tsx` | Loading skeleton |

Gemini must NOT touch:
- `frontend/lib/` — Codex owns all library code
- `frontend/types/` — Codex owns all type definitions
- `frontend/middleware.ts` — Codex owns middleware
- `backend/` — Codex owns all backend code
- `.ai/`, `tools/`, `status.json` — Claude owns orchestration

---

## Boundary Rules

1. Components (`frontend/components/`) must never call `propertiesApi.*` directly —
   data is fetched in pages and passed as props.
2. Pages (`frontend/app/`) must never call `fetch()` directly — all API calls go
   through `frontend/lib/api/properties.ts`.
3. No `@supabase/ssr` or `@supabase/supabase-js` imports in `components/` or `app/`.
4. `status.json` is written only by Claude. Any write by Codex or Gemini is a
   contract violation.
5. Report files (`codex-build-*.md`, `gemini-build-*.md`, `review.md`) are written by
   the wrapper script capturing stdout — workers must not create these files directly.
6. Codex may make one additive change to `backend/app/main.py` (register the new
   router) — no other modifications to existing F0/F1 files.
7. Pages must not transform API response shape. If normalization or mapping is needed,
   it belongs in `frontend/lib/api/properties.ts`, not in `frontend/app/`.
