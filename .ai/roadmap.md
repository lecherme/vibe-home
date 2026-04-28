# Roadmap

Status legend: `[ ]` pending · `[~]` in progress · `[x]` done

---

## F0 — Foundation

**Status:** `[ ]`
**Owner:** Codex (skeleton) · Claude (acceptance)

**Goal:**
Establish the two-service structure (frontend + backend) with minimal runnable configuration so every subsequent feature has a consistent starting point.

**Non-Goals:**
- No application features
- No database schema beyond connection verification
- No authentication logic
- No search-service — search is an internal backend module until F3 needs it extracted

**Deliverables:**
- `frontend/` — Next.js app with App Router, Tailwind, shadcn initialized
- `backend/` — FastAPI app with `/health` endpoint, Supabase connection check, env config
- `.env.example` for frontend and backend
- `README.md` at repo root with local setup instructions

**Dependencies:** none

**Acceptance Criteria:**
- `GET /health` returns 200 on backend
- Frontend dev server starts without errors
- All env vars documented in `.env.example`

---

## F1 — Authentication & Roles

**Status:** `[ ]`
**Owner:** Codex (backend + auth client) · Gemini (login/signup UI) · Claude (acceptance)

**Goal:**
Users can register, log in, and log out. Every API request is authenticated. Two roles are supported at this stage: `user` and `admin`. Role is stored in Supabase and enforced by FastAPI.

**Non-Goals:**
- OAuth / social login
- Email verification flow
- Password reset UI (backend endpoint only, no UI)
- Fine-grained role variants (buyer vs agent distinction deferred to F6)
- Role management UI

**Deliverables:**
- Supabase Auth integration in FastAPI (JWT validation middleware)
- `/api/v1/auth/me` endpoint returning user + role
- Role stored in Supabase `profiles` table, seeded on signup
- `lib/auth/` client helpers in frontend
- Login and signup pages

**Dependencies:** F0

**Acceptance Criteria:**
- Unauthenticated requests to protected endpoints return 401
- Wrong-role requests return 403
- Login sets session; logout clears it
- `useCurrentUser` hook returns user object with role

---

## F2 — Property Browsing

**Status:** `[ ]`
**Owner:** Codex (backend) · Gemini (UI) · Claude (acceptance)

**Goal:**
Authenticated users can browse a paginated list of property listings and view a detail page for each property.

**Non-Goals:**
- Search or filtering (F3)
- Favorites (F4)
- Admin editing (F5)
- Map view

**Deliverables:**
- `properties` table in Supabase with seed data
- `GET /api/v1/properties` — paginated list endpoint
- `GET /api/v1/properties/{id}` — detail endpoint
- `PropertyRead` Pydantic schema published to `frontend/types/`
- Property list page with pagination controls
- Property detail page

**Dependencies:** F1

**Acceptance Criteria:**
- List returns paginated results (page, page_size, total)
- Detail returns full property object or 404
- UI renders list and detail without errors on seed data
- Unauthenticated access returns 401

---

## F3 — Search & Filtering

**Status:** `[ ]`
**Owner:** Codex (search module + FastAPI integration) · Gemini (search UI) · Claude (acceptance)

**Goal:**
Users can filter properties by location, price range, and bedroom count. Search logic lives in an internal backend module. The module may be extracted to `search-service/` if complexity warrants it, but that is a deployment decision, not a requirement. F3 implements search/filter only on existing Property schema fields.

**Non-Goals:**
- Natural language / AI search (F7)
- Saved searches
- Sort order customization beyond default relevance
- Extracting search-service as a separate process (optional, not required)
- Property type filtering — deferred: requires Property schema property_type field extension, seed data updates, and frontend type sync; will be scoped in a separate feature

**Deliverables:**
- `backend/app/services/search/` — internal search module accepting structured filters, returning ranked property IDs
- FastAPI: `GET /api/v1/properties/search` — validates input, calls search module, returns hydrated results
- `SearchFilters` and `SearchResult` types published to `frontend/types/`
- Search bar and filter panel components
- Results page wired to search endpoint

**Dependencies:** F2

**Acceptance Criteria:**
- Filters applied in UI are reflected in API query
- Empty filter set returns all properties (paginated)
- Frontend never calls search logic directly — all search goes through FastAPI
- Invalid filter values return 422

---

## F4 — Favorites

**Status:** `[ ]`
**Owner:** Codex (backend) · Gemini (UI) · Claude (acceptance)

**Goal:**
Authenticated users can save and unsave property listings and view their saved listings in a dedicated page.

**Non-Goals:**
- Sharing favorites with other users
- Favorites folders or tags
- Notifications on saved listings

**Deliverables:**
- `favorites` table in Supabase (user_id, property_id, created_at)
- `POST /api/v1/favorites/{property_id}` — add favorite
- `DELETE /api/v1/favorites/{property_id}` — remove favorite
- `GET /api/v1/favorites` — list user's favorites
- Favorite toggle button on property card and detail page
- Favorites page

**Dependencies:** F2

**Acceptance Criteria:**
- Toggle is optimistic — UI updates before server confirms
- Duplicate favorites return 409
- Favorites are user-scoped — users cannot see others' favorites
- Admin role cannot access favorites endpoints (403)

---

## F5 — Admin Property Management

**Status:** `[ ]`
**Owner:** Codex (backend) · Gemini (admin UI) · Claude (acceptance)

**Goal:**
Admin users can create, edit, and delete property listings through a dedicated admin interface.

**Non-Goals:**
- Bulk import / CSV upload
- Image upload (placeholder image URL only)
- Audit log / change history
- Draft / publish workflow

**Deliverables:**
- `POST /api/v1/admin/properties` — create listing
- `PUT /api/v1/admin/properties/{id}` — update listing
- `DELETE /api/v1/admin/properties/{id}` — delete listing
- All admin endpoints enforce `role=admin`
- Admin property list page with edit/delete actions
- Property create/edit form

**Dependencies:** F1, F2

**Acceptance Criteria:**
- Non-admin requests to admin endpoints return 403
- Create and update validate required fields (422 on missing)
- Deleted properties no longer appear in browse or search
- Form shows validation errors inline

---

## F6 — Access Control

**Status:** `[ ]`
**Owner:** Codex (backend hardening) · Claude (acceptance)

**Goal:**
Audit and harden all endpoints to ensure RBAC is consistently enforced. Define and document the permission matrix. Introduce buyer/agent role distinction if needed.

**Non-Goals:**
- New user-facing features
- UI changes
- Fine-grained per-resource permissions (row-level security is Supabase-managed)

**Deliverables:**
- Permission matrix documented in `.ai/permissions.md`
- All endpoints verified against matrix
- Integration tests covering each role × endpoint combination
- Any gaps found in F1–F5 fixed

**Dependencies:** F1, F2, F3, F4, F5

**Acceptance Criteria:**
- Every endpoint has a documented expected behavior per role
- No endpoint returns 200 for a role that should be denied
- Test suite covers all role × endpoint combinations

---

## F7 — AI Search / RAG

**Status:** `[ ]`
**Owner:** Codex (search service upgrade + embedding pipeline) · Claude (acceptance)

**Goal:**
Users can submit natural language queries and receive semantically ranked results. The upgrade is contained entirely within the search boundary — FastAPI's interface and the frontend are unchanged.

**Non-Goals:**
- Conversational / multi-turn search
- LLM-generated property descriptions
- Changes to FastAPI's call interface to the search boundary
- Changes to the frontend search UI (reuses F3 components)

**Deliverables:**
- Search module extracted to `search-service/` (required for this phase)
- pgvector extension enabled in Supabase
- Embedding generation on property create/update (async background job)
- Search Service: natural language query → embedding → ANN search → ranked IDs
- RAG layer: top-k listings passed to LLM for optional summary response
- Feature flag `SEARCH_AI_ENABLED` to toggle between FTS and AI search

**Dependencies:** F3, F6

**Acceptance Criteria:**
- Natural language query returns relevant results
- Feature flag off → behavior identical to F3
- FastAPI's internal call to search boundary is unchanged
- Embedding pipeline does not block the write path (async)
