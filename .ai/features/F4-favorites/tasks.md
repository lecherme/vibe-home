# Favorites — Tasks

Every task has exactly one owner. Collaboration happens through sequential tasks, not shared tasks.

---

## T01 — Scaffold favorites backend schemas and service skeleton

- **owner:** codex
- **type:** scaffold
- **depends_on:** none
- **title:** Scaffold favorites Pydantic schemas and service skeleton

**Scope:**
- Create `backend/app/schemas/favorite.py` with:
  - FavoriteRead schema (property_id: str, user_id: str, created_at: str)
  - FavoriteList schema (items: List[PropertyRead], total: int)
- Create `backend/app/services/favorites/__init__.py`
- Create `backend/app/services/favorites/service.py` with:
  - Module-level in-memory store: dict mapping user_id → set of property_ids
  - Stub method signatures: add_favorite(), remove_favorite(), get_user_favorites()
  - No implementation logic — stubs only

**Allowed file changes:**
- Create: `backend/app/schemas/favorite.py`
- Create: `backend/app/services/favorites/__init__.py`
- Create: `backend/app/services/favorites/service.py`

**Done condition:** All three files exist with correct Pydantic schemas and function stubs; no syntax errors.

---

## T02 — Implement favorites endpoints and tests

- **owner:** codex
- **type:** backend
- **depends_on:** T01
- **title:** Implement POST/DELETE/GET favorites endpoints with auth and tests

**Scope:**
- Implement full logic in `backend/app/services/favorites/service.py`:
  - add_favorite(user_id, property_id): add to store; raise HTTPException 409 if already present
  - remove_favorite(user_id, property_id): remove from store; raise HTTPException 404 if not found
  - get_user_favorites(user_id, page, page_size): return FavoriteList with paginated PropertyRead items
- Create `backend/app/api/v1/favorites/__init__.py`
- Create `backend/app/api/v1/favorites/router.py` with:
  - POST /api/v1/favorites/{property_id} → 201, requires user auth, 403 for admin
  - DELETE /api/v1/favorites/{property_id} → 204, requires user auth, 403 for admin
  - GET /api/v1/favorites → 200 FavoriteList, requires user auth, 403 for admin
  - All endpoints: 401 if not authenticated
- Modify `backend/app/main.py` to include the favorites router at /api/v1/favorites
- Create `backend/tests/test_favorites.py` covering:
  - POST adds favorite and returns 201
  - POST duplicate returns 409
  - DELETE removes favorite and returns 204
  - GET returns only the current user's favorites (not another user's)
  - All endpoints return 401 unauthenticated
  - All endpoints return 403 for admin role

**Allowed file changes:**
- Modify: `backend/app/services/favorites/service.py`
- Create: `backend/app/api/v1/favorites/__init__.py`
- Create: `backend/app/api/v1/favorites/router.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_favorites.py`

**Done condition:** All tests pass; endpoints correctly handle auth, role, duplicate, 404, and user-scope cases.

---

## T03 — Publish frontend types and typed API wrapper

- **owner:** codex
- **type:** infra
- **depends_on:** T02
- **title:** Publish frontend types and typed favorites API wrapper

**Scope:**
- Create `frontend/types/favorites.ts` with:
  - Favorite interface (propertyId: string, userId: string, createdAt: string)
  - FavoriteList interface (items: PropertyRead[], total: number)
- Create `frontend/lib/api/favorites.ts` with exactly three functions:
  - addFavorite(propertyId: string): Promise<void>
  - removeFavorite(propertyId: string): Promise<void>
  - getFavorites(page?: number, pageSize?: number): Promise<FavoriteList>
- Do NOT add an isFavorite() or status-check function — whether a property is currently favorited
  is UI-local state managed by T04, not a backend call.
- Ensure all types are exported and usable by the UI layer

**Allowed file changes:**
- Create: `frontend/types/favorites.ts`
- Create: `frontend/lib/api/favorites.ts`

**Done condition:** TypeScript compiles without errors; three API functions exist with correct signatures; types match backend schemas; no isFavorite backend call introduced.

---

## T04 — Implement favorites UI

- **owner:** gemini
- **type:** ui
- **depends_on:** T02, T03
- **title:** Implement FavoriteButton component, favorites page, and integrate into property card and detail

**Scope:**
- Create `frontend/components/features/favorites/favorite-button.tsx`:
  - Renders a heart/bookmark icon button
  - Accepts props: propertyId: string, initialIsFavorited?: boolean (default false)
  - Manages isFavorited boolean state locally — this is purely local UI state, no separate
    backend status-check call required
  - Optimistic update: toggle local state immediately, then call API; on error revert state
  - On toggle to favorited: call favoritesApi.addFavorite(propertyId)
  - On toggle to unfavorited: call favoritesApi.removeFavorite(propertyId)
- Create `frontend/app/(dashboard)/favorites/page.tsx`:
  - Fetch user's favorites on mount via favoritesApi.getFavorites()
  - Display results using PropertyCard components
  - Loading skeleton while fetching
  - Empty state when no favorites
  - Error state if API call fails
- Modify `frontend/components/features/properties/property-card.tsx`:
  - Import and render <FavoriteButton propertyId={property.id} /> on the card
- Modify `frontend/app/(dashboard)/properties/[id]/page.tsx`:
  - Import and render <FavoriteButton propertyId={property.id} /> on the detail page
- Use lib/api/favorites only — no direct fetch() or Supabase calls

**Allowed file changes:**
- Create: `frontend/components/features/favorites/favorite-button.tsx`
- Create: `frontend/app/(dashboard)/favorites/page.tsx`
- Modify: `frontend/components/features/properties/property-card.tsx`
- Modify: `frontend/app/(dashboard)/properties/[id]/page.tsx`

**Done condition:** Favorites page renders; toggle button appears on card and detail; optimistic update works; loading, empty, and error states present; TypeScript compiles clean.

---

## T05 — Codex review

- **owner:** codex
- **type:** review
- **depends_on:** T01, T02, T03, T04
- **title:** Review F4-favorites implementation against acceptance criteria

**Scope:**
- Validate all implementation deliverables against `acceptance.md`.
- Check ownership boundaries and task artifacts.
- Verify user-scoping (A6) and admin exclusion (A8).
- Verify optimistic update pattern (A15).
- Verify no extra backend status-check endpoint was added.
- Write `review.md`.

**Done condition:** `review.md` written with a verdict, per-criterion results, and enough failure detail for Claude to choose task_retry, direct_fixup, or review_rerun.

---

## T06 — Claude acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T05
- **title:** Validate F4-favorites and write final acceptance result

**Scope:**
- Read `review.md`.
- Write `final-report.md` with disposition `accepted` or `failed`.
- Update `status.json` feature status to `done` or `failed`.

**Done condition:** `final-report.md` written and `status.json` updated.
