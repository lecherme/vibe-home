# Search & Filtering

## Goal

Users can filter properties by location, price range, and bedroom count. Search logic lives in an internal backend module within `backend/app/services/search/`. The module may be extracted to `search-service/` in future if complexity warrants it, but that is a deployment decision, not a requirement for this feature. F3 implements search/filter only on existing Property schema fields.

## Scope

### Backend Deliverables
- `backend/app/services/search/` — internal search module accepting structured filters, returning ranked property IDs
- `GET /api/v1/properties/search` — validates input, calls search module, returns hydrated results
- `SearchFilters` and `SearchResult` Pydantic schemas

### Frontend Deliverables
- `SearchFilters` and `SearchResult` types published to `frontend/types/`
- `lib/api/properties.ts` — typed fetch wrapper for search endpoint
- Search bar component (`components/features/search/search-bar.tsx`)
- Filter panel component (`components/features/search/filter-panel.tsx`)
- Search results page (`app/(main)/search/page.tsx`) wired to search endpoint

## Non-Goals

- Natural language / AI search (deferred to F7)
- Saved searches
- Sort order customization beyond default relevance
- Extracting search-service as a separate process (optional deployment decision, not required)
- Map view integration
- Property type filtering — deferred: Property schema has no property_type field; requires backend schema extension, seed data updates, and frontend type sync; will be scoped in a separate feature

## Constraints

- All implementation must follow `.ai/conventions.md` and `.ai/orchestration.md`.
- Workers must implement only their assigned task.
- `status.json` is updated only by Claude Code orchestration.
- Frontend must never call search logic directly — all search goes through FastAPI.

## Dependencies

- **F2 (Property Browsing)** — required status: `done`
  - Depends on `properties` table and PropertyRead schema
  - Depends on existing property list and detail pages
  - Depends on `lib/api/properties.ts` typed fetch wrappers

## Required Env Vars

No new env vars.
