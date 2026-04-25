# F2 — Property Browsing

## Goal

Allow authenticated users to browse a paginated list of properties and view a single
property's detail page. This is the first feature that introduces real application data
and establishes the canonical read-pattern all future features must follow:

- authenticated API access via FastAPI boundary (`get_current_user` dependency)
- typed frontend API client abstraction (`lib/api/`)
- page-level data fetching with purely presentational components
- future features (search, favourites, admin) must reuse this pattern — no ad-hoc fetch
  calls or direct Supabase access in pages or components

## Scope

### Backend
- `Property` Pydantic schema: `id`, `title`, `description`, `price`, `location`,
  `bedrooms`, `bathrooms`, `area_sqm`, `images` (list of URLs), `status`
  (`available` | `sold` | `rented`), `created_at`
- In-memory property store (list of seed fixtures) — no database yet
- `GET /api/v1/properties` — paginated list (query params: `page`, `page_size`, max 50)
  - Returns `{ items: Property[], total: int, page: int, page_size: int }`
  - Results sorted by `created_at` descending
  - If `page` exceeds available range, returns empty `items` with valid `total`, `page`, `page_size`
  - Protected: requires valid JWT (`get_current_user`)
- `GET /api/v1/properties/{id}` — single property by ID
  - Protected: requires valid JWT
  - Returns 404 if not found
- Unit tests covering: list pagination, single fetch, 404, 401 without token
- Types published to `frontend/types/property.ts`

### Frontend
- `lib/api/properties.ts` — typed fetch wrappers:
  - `propertiesApi.list(page, pageSize): Promise<PropertyListResponse>`
  - `propertiesApi.get(id): Promise<Property>`
- `app/(dashboard)/properties/page.tsx` — property list page:
  - Fetches via `propertiesApi.list`
  - Renders `<PropertyCard />` grid
  - Pagination controls (previous / next)
  - Loading skeleton state
  - Empty state when no results
  - Explicit error state with user-friendly message when API call fails
- `app/(dashboard)/properties/[id]/page.tsx` — property detail page:
  - Fetches via `propertiesApi.get`
  - Renders `<PropertyDetail />`
  - 404 handling via `notFound()`
- `app/(dashboard)/layout.tsx` — authenticated shell layout (nav bar placeholder)
- `components/features/properties/PropertyCard.tsx` — card component (image, title,
  price, location, bedrooms/bathrooms badges)
- `components/features/properties/PropertyDetail.tsx` — full detail component
- `components/features/properties/PropertyListSkeleton.tsx` — loading skeleton
- Basic Tailwind styling; no custom design system yet

### Shared
- `frontend/types/property.ts` — `Property`, `PropertyStatus`, `PropertyListResponse`
  TypeScript types (mirrored from backend schema)

## Non-Goals

- Property creation, editing, or deletion (deferred to admin feature)
- Map / geo views (deferred)
- Search and filtering (deferred to F3)
- Favourites / saved properties (deferred)
- Real database (deferred — in-memory seed data only for now)
- Image upload (deferred)

## Constraints

- All data fetching in pages goes through `lib/api/properties.ts` — no direct `fetch()`
  in components or pages
- Components receive data as props — no data fetching inside components
- Backend endpoints are protected — unauthenticated requests return 401
- No hardcoded credentials or production URLs in source
- `status.json` written only by Claude
- Pagination: default `page=1`, default `page_size=12`, max `page_size=50`

## Dependencies

- F1 must be `done` (auth middleware and `get_current_user` dependency required)

## Required Env Vars

No new env vars. Existing `NEXT_PUBLIC_API_URL` covers the backend base URL.
