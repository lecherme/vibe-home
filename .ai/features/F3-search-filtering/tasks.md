# Search & Filtering — Tasks

Every task has exactly one owner. Collaboration happens through sequential tasks, not shared tasks.

---

## T01 — Scaffold search module structure and schemas

- **owner:** codex
- **type:** scaffold
- **depends_on:** none
- **title:** Scaffold search module structure and Pydantic schemas

**Scope:**
- Create `backend/app/services/search/__init__.py`
- Create `backend/app/services/search/service.py` with empty search() function stub (accepts filters and db session, returns List[int])
- Create `backend/app/schemas/search.py` with:
  - SearchFilters Pydantic schema (location: Optional[str], min_price: Optional[int], max_price: Optional[int], bedrooms: Optional[int], status: Optional[str])
  - SearchResult Pydantic schema (items: List[PropertyRead], total: int, page: int, page_size: int)
- No actual query logic — only type stubs and schema definitions

**Allowed file changes:**
- Create: `backend/app/services/search/__init__.py`
- Create: `backend/app/services/search/service.py`
- Create: `backend/app/schemas/search.py`

**Done condition:** All three files exist with correct Pydantic schemas and function stub; no syntax errors.

---

## T02 — Implement search module and API endpoint

- **owner:** codex
- **type:** backend
- **depends_on:** T01
- **title:** Implement search service and GET /api/v1/properties/search

**Scope:**
- Implement `backend/app/services/search/service.py` search() function with filter logic:
  - Filter by location (case-insensitive substring match on address or city)
  - Filter by price range (price between min_price and max_price if provided)
  - Filter by bedrooms (bedrooms >= filter value if provided)
  - Filter by status (exact match if provided)
  - Return List[int] of matching property IDs
- Modify `backend/app/api/v1/properties/router.py` to add:
  - GET /api/v1/properties/search endpoint accepting SearchFilters as query params
  - Call search service, hydrate PropertyRead objects from IDs
  - Return SearchResult with items, total, page, page_size
  - Pagination: page (default 1), page_size (default 20), limit page_size to 100
- Add tests in `backend/tests/test_search.py` covering:
  - Empty filters returns all properties (paginated)
  - Location filter matches substring
  - Price range filter inclusive
  - Bedrooms filter is >=
  - Status filter exact match
  - Invalid filter values return 422 (negative price, invalid status)
  - Page size cap at 100

**Allowed file changes:**
- Modify: `backend/app/services/search/service.py`
- Modify: `backend/app/api/v1/properties/router.py` (add /search endpoint)
- Create: `backend/tests/test_search.py`

**Done condition:** All tests pass; search endpoint returns correct filtered results; pagination works; invalid inputs return 422.

---

## T03 — Publish types and API wrapper

- **owner:** codex
- **type:** infra
- **depends_on:** T02
- **title:** Publish frontend types and typed search API wrapper

**Scope:**
- Create `frontend/types/search.ts` with SearchFilters and SearchResult interfaces mirroring backend Pydantic schemas
- Modify `frontend/lib/api/properties.ts` to add:
  - `searchProperties(filters: SearchFilters, page?: number, pageSize?: number): Promise<SearchResult>`
- Ensure types are exported and usable by UI layer

**Allowed file changes:**
- Create: `frontend/types/search.ts`
- Modify: `frontend/lib/api/properties.ts`

**Done condition:** TypeScript compiles without errors; search function exists with correct signature; types match backend schemas.

---

## T04 — Implement search UI components and page

- **owner:** gemini
- **type:** ui
- **depends_on:** T02, T03
- **title:** Implement search bar, filter panel, and search results page

**Scope:**
- Create `frontend/app/(dashboard)/search/page.tsx` with:
  - Search input (location text field)
  - Filter panel: min_price, max_price, bedrooms, status dropdown
  - Search button to trigger API call
  - Results display: property cards from search result items
  - Pagination controls (prev/next buttons with page indicator)
  - Loading state while API call in progress
  - Error state display
- Create `frontend/components/features/search/search-bar.tsx` (location input + search button)
- Create `frontend/components/features/search/filter-panel.tsx` (price range, bedrooms, status inputs)
- Reuse `frontend/components/features/properties/property-card.tsx` from F2 for result display
- Use `lib/api/properties.searchProperties()` for API calls
- State management: React useState for filters and results
- No Supabase imports; no direct API calls outside lib/api/

**Allowed file changes:**
- Create: `frontend/app/(dashboard)/search/page.tsx`
- Create: `frontend/components/features/search/search-bar.tsx`
- Create: `frontend/components/features/search/filter-panel.tsx`
- Read-only: `frontend/components/features/properties/property-card.tsx` (reuse only)

**Done condition:** Page renders without errors; search and filters work; results display correctly; pagination functional; loading and error states present.

---

## T05 — Codex review

- **owner:** codex
- **type:** review
- **depends_on:** T01, T02, T03, T04
- **title:** Review F3-search-filtering implementation against acceptance criteria

**Scope:**
- Validate all implementation deliverables against `acceptance.md`.
- Check ownership boundaries and task artifacts.
- Verify no property_type filtering was implemented (deferred).
- Write `review.md`.

**Done condition:** `review.md` written with a verdict, per-criterion results, and enough failure detail for Claude to choose task_retry, direct_fixup, or review_rerun.

---

## T06 — Claude acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T05
- **title:** Validate F3-search-filtering and write final acceptance result

**Scope:**
- Read `review.md`.
- Write `final-report.md` with disposition `accepted` or `failed`.
- Update `status.json` feature status to `done` or `failed`.

**Done condition:** `final-report.md` written and `status.json` updated.
