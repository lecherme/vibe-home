# F2 — Tasks

Every task has exactly one owner. Collaboration happens through sequential tasks, not shared tasks.

---

## T01 — Backend property schema and seed data

- **owner:** codex
- **type:** scaffold
- **depends_on:** none
- **title:** Define Property schema, seed fixtures, and in-memory store

**Scope:**
- Create `backend/app/schemas/property.py`:
  - `PropertyStatus` enum: `available`, `sold`, `rented`
  - `Property` Pydantic model: `id` (str), `title`, `description`, `price` (float),
    `location`, `bedrooms` (int), `bathrooms` (int), `area_sqm` (float),
    `images` (list[str]), `status` (PropertyStatus), `created_at` (datetime)
  - `PropertyListResponse`: `items` (list[Property]), `total` (int), `page` (int),
    `page_size` (int)
- Create `backend/app/data/properties.py`:
  - In-memory list of at least 15 seed `Property` fixtures with realistic data
  - `get_all() -> list[Property]`
  - `get_by_id(id: str) -> Property | None`
- Write `frontend/types/property.ts` with `Property`, `PropertyStatus`,
  `PropertyListResponse` TypeScript types mirroring the backend schema

**Done condition:** Schema importable without errors; seed data has ≥ 15 items;
`frontend/types/property.ts` exists with correct types

---

## T02 — Backend property endpoints

- **owner:** codex
- **type:** backend
- **depends_on:** T01
- **title:** Implement GET /api/v1/properties and GET /api/v1/properties/{id}

**Scope:**
- Create `backend/app/api/v1/properties/` with `__init__.py` and `router.py`
- `GET /api/v1/properties`:
  - Query params: `page: int = 1`, `page_size: int = 12` (max 50, clamp silently)
  - Protected by `get_current_user`
  - Returns `PropertyListResponse`
- `GET /api/v1/properties/{id}`:
  - Protected by `get_current_user`
  - Returns `Property` or `HTTPException(404)`
- Register router in `backend/app/main.py` under `/api/v1/properties`
- Write unit tests in `backend/tests/test_properties.py`:
  - List returns paginated results with correct `total`, `page`, `page_size`
  - List results are sorted by `created_at` descending
  - `page_size` clamped to 50 when exceeded
  - Page beyond available range returns empty `items` with valid `total`, `page`, `page_size`
  - Single fetch returns correct property
  - Single fetch returns 404 for unknown ID
  - Both endpoints return 401 without a valid JWT

**Done condition:** All tests pass; both endpoints registered and reachable

---

## T03 — Frontend property API library

- **owner:** codex
- **type:** infra
- **depends_on:** T01
- **title:** Implement lib/api/properties.ts typed fetch wrappers

**Scope:**
- Create `frontend/lib/api/properties.ts`:
  - `propertiesApi.list(page: number, pageSize: number): Promise<PropertyListResponse>`
    — `GET /api/v1/properties?page=&page_size=` with Bearer token
  - `propertiesApi.get(id: string): Promise<Property>`
    — `GET /api/v1/properties/{id}` with Bearer token
  - Both functions retrieve the access token via `getAccessToken()` from
    `lib/auth/session.ts` and attach it as `Authorization: Bearer <token>`
  - Both functions throw on non-2xx responses; error must include HTTP status code and
    message so the UI can handle them appropriately

Retry note:
- Fix review blocker L3 from review.md.
- In frontend/lib/api/properties.ts, every thrown PropertyApiError.message must include the HTTP status code.
- This must include:
  - the no-session 401 path
  - the res.status error path
- Storing the code only on PropertyApiError.status is NOT sufficient; the message text itself must contain the code.
- Acceptable examples:
  - "HTTP 401: No active session"
  - "HTTP 404: Not found"

**Done condition:** TypeScript compiles without errors; no direct `fetch()` outside
`lib/api/`; access token sourced only from `lib/auth/session.ts`

---

## T04 — Property list and detail pages

- **owner:** gemini
- **type:** ui
- **depends_on:** T02, T03
- **title:** Implement property list page, detail page, and dashboard layout

**Scope:**
- Create `frontend/app/(dashboard)/layout.tsx`:
  - Authenticated shell with a minimal top nav bar (app name + sign-out link)
  - No business logic — layout only
- Create `frontend/app/(dashboard)/properties/page.tsx`:
  - Use page-level data fetching; avoid data fetching inside components
  - Client components are allowed only for interactive UI state (e.g. pagination controls) if needed
  - Fetches via `propertiesApi.list`; passes data to `<PropertyCard />` grid
  - Pagination controls: previous / next buttons; disabled at boundaries
  - Loading skeleton: renders `<PropertyListSkeleton />` while fetching
  - Empty state: clear message when `items` is empty
  - Error state: user-friendly message when API call fails
- Create `frontend/app/(dashboard)/properties/[id]/page.tsx`:
  - Fetches via `propertiesApi.get(id)`
  - Renders `<PropertyDetail />`
  - Calls `notFound()` on 404 response
- Create `frontend/components/features/properties/PropertyCard.tsx`:
  - Props: `property: Property`
  - Displays: first image (or placeholder), title, price, location, bedrooms,
    bathrooms badges
  - Entire card is a link to `/properties/{id}`
  - No data fetching
- Create `frontend/components/features/properties/PropertyDetail.tsx`:
  - Props: `property: Property`
  - Displays: image gallery (or single image), title, price, location, full
    description, bedrooms, bathrooms, area, status badge
  - No data fetching
- Create `frontend/components/features/properties/PropertyListSkeleton.tsx`:
  - Renders a grid of placeholder skeleton cards matching `PropertyCard` layout
  - Pure presentational — no props required

**Absolute constraints (contract — any violation is a blocker):**
- Do NOT import from `@supabase/ssr` or `@supabase/supabase-js` in `components/` or `app/`
- Do NOT call `fetch()` directly — all API calls must go through `lib/api/properties.ts`
- Do NOT call `propertiesApi.*` inside components — data is passed as props
- Do NOT write business logic in components — only rendering and UI state
- Do NOT transform API response shape in pages — normalization belongs in `lib/api/properties.ts`
- Do NOT modify `frontend/lib/`, `frontend/types/`, `frontend/middleware.ts`, or any backend file

**Done condition:** Pages render without errors; list shows paginated cards; detail shows
full property; loading and empty states handled; no direct fetch or Supabase calls in
components or pages

---

## T05 — Codex review

- **owner:** codex
- **type:** review
- **depends_on:** T01, T02, T03, T04
- **title:** Review F2 implementation against acceptance criteria

**Scope:**
- Validate all T01–T04 deliverables against `acceptance.md`
- Check for boundary violations (direct fetch in components, Supabase imports outside lib)
- Verify pagination logic, 404 handling, and 401 enforcement
- Verify TypeScript compiles without errors
- Write `review.md`

**Done condition:** `review.md` written with a verdict and per-criterion results

---

## T06 — Claude acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T05
- **title:** Validate F2 and write final acceptance result

**Scope:**
- Read `review.md` produced by T05
- Verify all acceptance criteria in `acceptance.md` are addressed
- Write `final-report.md` with disposition `accepted` or `failed`
- If `failed`: note specific failing criteria and return affected tasks to `pending`
  in `status.json`
- Update `status.json` feature status to `done` or `failed`

**Done condition:** `final-report.md` written with a clear disposition; `status.json`
updated to reflect final feature state
