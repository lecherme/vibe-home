# Favorites — Ownership Boundaries

This is a static ownership map. Runtime state comes from `status.json`.

## Codex

**Owns:**
- `backend/app/schemas/favorite.py` — FavoriteRead, FavoriteList Pydantic schemas
- `backend/app/services/favorites/__init__.py` — service package init
- `backend/app/services/favorites/service.py` — favorites service implementation
- `backend/app/api/v1/favorites/__init__.py` — router package init
- `backend/app/api/v1/favorites/router.py` — POST, DELETE, GET endpoints
- `backend/app/main.py` — router registration only (minimal change)
- `backend/tests/test_favorites.py` — favorites endpoint tests
- `frontend/types/favorites.ts` — Favorite, FavoriteList, and FavoriteStatus TypeScript interfaces
- `frontend/lib/api/favorites.ts` — addFavorite(), removeFavorite(), getFavorites(), isFavorite() wrappers

**Must NOT:**
- Create or modify UI components or pages
- Modify shadcn primitives in `components/ui/`
- Modify frontend files outside `types/` and `lib/api/`

## Gemini

**Owns:**
- `frontend/app/(dashboard)/favorites/page.tsx` — favorites listing page
- `frontend/components/features/favorites/favorite-button.tsx` — optimistic toggle button
- `frontend/components/features/properties/PropertyCard.tsx` — modify to add FavoriteButton
- `frontend/app/(dashboard)/properties/[id]/page.tsx` — modify to add FavoriteButton

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
4. Favorites endpoints must live in a dedicated `/api/v1/favorites/` router, not added to the properties router.
5. Favorites page must be in the `(dashboard)` route group.
6. Admin role must be denied (403) on all favorites endpoints.
