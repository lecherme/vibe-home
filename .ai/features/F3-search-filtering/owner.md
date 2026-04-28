# Search & Filtering — Ownership Boundaries

This is a static ownership map. Runtime state comes from `status.json`.

## Codex

**Owns:**
- `backend/app/services/search/` — search module implementation
- `backend/app/schemas/search.py` — SearchFilters and SearchResult Pydantic schemas
- `backend/app/api/v1/properties/router.py` — GET /api/v1/properties/search endpoint
- `backend/tests/test_search.py` — search endpoint and service tests
- `frontend/types/search.ts` — SearchFilters and SearchResult TypeScript interfaces
- `frontend/lib/api/properties.ts` — searchProperties() typed fetch wrapper

**Must NOT:**
- Create or modify UI components or pages
- Modify shadcn primitives in `components/ui/`
- Create new API routers outside properties scope

## Gemini

**Owns:**
- `frontend/app/(dashboard)/search/page.tsx` — search results page
- `frontend/components/features/search/search-bar.tsx` — search input component
- `frontend/components/features/search/filter-panel.tsx` — filter inputs component

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
4. Search endpoint must be added to existing properties router, not a separate search router.
5. Search page must be in `(dashboard)` route group, not a new route group.
6. Property type filtering is explicitly deferred — no implementation in this feature.
