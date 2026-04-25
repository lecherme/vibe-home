# F2 — Acceptance Criteria

T05 (Codex review) verifies every criterion below and writes `review.md`.
T06 (Claude acceptance) reads `review.md` and writes `final-report.md` with the final disposition.

---

## Backend Schema & Seed Data (T01)

| # | Criterion | Check |
|---|-----------|-------|
| D1 | `backend/app/schemas/property.py` defines `PropertyStatus`, `Property`, and `PropertyListResponse` | Verify file and field names |
| D2 | `Property` has all required fields: `id`, `title`, `description`, `price`, `location`, `bedrooms`, `bathrooms`, `area_sqm`, `images`, `status`, `created_at` | Check schema fields and types |
| D3 | `PropertyStatus` enum has values `available`, `sold`, `rented` | Check enum values |
| D4 | `backend/app/data/properties.py` contains ≥ 15 seed fixtures | Count items in seed list |
| D5 | `get_all()` and `get_by_id(id)` are exported from `backend/app/data/properties.py` | Check function signatures |
| D6 | `frontend/types/property.ts` defines `Property`, `PropertyStatus`, `PropertyListResponse` mirroring backend schema | Check types match |

## Backend Endpoints (T02)

| # | Criterion | Check |
|---|-----------|-------|
| E1 | `backend/app/api/v1/properties/` exists with `__init__.py` and `router.py` | Verify files exist |
| E2 | `GET /api/v1/properties` returns `PropertyListResponse` with correct `total`, `page`, `page_size` | Check unit test |
| E3 | `GET /api/v1/properties` paginates correctly — `page=2, page_size=5` returns items 6–10 | Check unit test |
| E4 | `page_size` is clamped to 50 when a larger value is requested | Check unit test |
| E5 | Results are sorted by `created_at` descending | Check unit test |
| E6 | Page beyond available range returns empty `items` with valid `total`, `page`, `page_size` | Check unit test |
| E7 | `GET /api/v1/properties/{id}` returns the correct `Property` for a known ID | Check unit test |
| E8 | `GET /api/v1/properties/{id}` returns 404 for an unknown ID | Check unit test |
| E9 | Both endpoints return 401 when called without a valid JWT | Check unit test |
| E10 | Properties router registered in `backend/app/main.py` under `/api/v1/properties` | Check router include |
| E11 | All unit tests in `backend/tests/test_properties.py` pass | Run test suite |

## Frontend API Library (T03)

| # | Criterion | Check |
|---|-----------|-------|
| L1 | `frontend/lib/api/properties.ts` exports `propertiesApi.list` and `propertiesApi.get` | Check file and exports |
| L2 | Both functions attach `Authorization: Bearer <token>` using `getAccessToken()` from `lib/auth/session.ts` | Check implementation — no other token source |
| L3 | Both functions throw on non-2xx responses with a message containing the HTTP status code | Check error handling |
| L4 | No direct `fetch()` calls outside `frontend/lib/api/` | Grep for `fetch(` in `app/` and `components/` — must be absent |
| L5 | TypeScript compiles without errors across all T03 files | `tsc --noEmit` |

## Frontend UI (T04)

| # | Criterion | Check |
|---|-----------|-------|
| U1 | `frontend/app/(dashboard)/layout.tsx` exists with a nav bar | Check file |
| U2 | `frontend/app/(dashboard)/properties/page.tsx` exists and renders `<PropertyCard />` grid | Check file |
| U3 | List page renders `<PropertyListSkeleton />` during loading | Check loading state handling |
| U4 | List page renders an empty state message when `items` is empty | Check empty state handling |
| U5 | List page renders a user-friendly error message when the API call fails | Check error state handling |
| U6 | List page has previous / next pagination controls disabled at boundaries | Check pagination logic |
| U7 | `frontend/app/(dashboard)/properties/[id]/page.tsx` exists and renders `<PropertyDetail />` | Check file |
| U8 | Detail page calls `notFound()` on 404 response | Check 404 handling |
| U9 | `frontend/components/features/properties/PropertyCard.tsx` exists; renders image, title, price, location, bedrooms, bathrooms; entire card links to `/properties/{id}` | Check component |
| U10 | `frontend/components/features/properties/PropertyDetail.tsx` exists; renders full property data | Check component |
| U11 | `frontend/components/features/properties/PropertyListSkeleton.tsx` exists; pure presentational | Check component |
| U12 | No `propertiesApi.*` calls inside components — data passed as props only | Grep for `propertiesApi` in `components/` — must be absent |
| U13 | No direct `fetch()` in `app/` or `components/` | Grep for `fetch(` — must be absent |

---

## Boundary Enforcement (all tasks)

| # | Criterion | Check |
|---|-----------|-------|
| B1 | No `@supabase/ssr` or `@supabase/supabase-js` imports in `frontend/components/` or `frontend/app/` | Grep — must be absent |
| B2 | No hardcoded secrets, API keys, or production URLs in source files | Grep — must be absent |
| B3 | `status.json` was not modified by Codex or Gemini | Check git diff on `status.json` |
| B4 | Codex made no modifications to existing F1 files (only additive change to `main.py`) | Check git diff on F1 files |
| B5 | No report files created directly by workers | Check that build reports were captured by wrapper, not written by worker |
| B6 | Pages do not transform API response shape — any normalization is in `frontend/lib/api/properties.ts` | Grep for data mapping logic in `app/` — must be absent |

---

## Review and Acceptance (T05 + T06)

If T05 verdict is FAIL, Claude must return the failed task(s) to `pending` in `status.json` before retry.

**T05 — Codex review** writes `review.md` containing:
- A per-criterion PASS/FAIL table covering D1–D6, E1–E11, L1–L5, U1–U13, B1–B6
- A list of issues found (BLOCKER / WARNING / MINOR)
- Required fixes for any blockers
- An overall verdict: PASS or FAIL

**T06 — Claude acceptance** reads `review.md` and writes `final-report.md` containing:
- Final disposition: `accepted` or `failed`
- If `failed`: the specific criteria that failed and which tasks must be retried
- Claude then updates `status.json` feature status to `done` or `failed`

---

## Rejection Conditions

Codex review (T05) must mark the verdict as **FAIL** if any of these are true:

- Any criterion above is not met
- Any component or page calls `propertiesApi.*` directly (data must be passed as props)
- Any component or page calls `fetch()` directly
- Any component or page imports from `@supabase/ssr` or `@supabase/supabase-js`
- Either endpoint is accessible without a valid JWT
- `page_size` is not clamped to 50
- `GET /api/v1/properties/{id}` does not return 404 for unknown IDs
- Hardcoded secrets or production URLs in any source file
- `status.json` was modified by Codex or Gemini
- Codex modified existing F1 files beyond the additive router registration in `main.py`
- Pages transform API response shape instead of delegating to `lib/api/properties.ts`
