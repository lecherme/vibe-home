# Favorites

## Goal

Authenticated users can save and unsave property listings and view their saved listings in a dedicated page. Favorites are user-scoped and not shareable. The feature adds a toggle button to existing property cards and detail pages, with optimistic UI updates.

## Scope

**Backend (Codex):**
- In-memory favorites store (user_id → set of property_ids)
- `POST /api/v1/favorites/{property_id}` — add favorite (201 on success, 409 on duplicate)
- `DELETE /api/v1/favorites/{property_id}` — remove favorite (204 on success)
- `GET /api/v1/favorites` — list user's favorited properties (returns paginated PropertyRead list)
- `GET /api/v1/favorites/{property_id}` — check if a single property is favorited; returns `{"is_favorite": bool}` (200); requires user auth (401/403)
- All endpoints require user authentication (401 if not authenticated, 403 if admin role)

**Frontend — Codex:**
- `frontend/types/favorites.ts` — Favorite, FavoriteList, and FavoriteStatus TypeScript interfaces
- `frontend/lib/api/favorites.ts` — addFavorite(), removeFavorite(), getFavorites(), isFavorite() typed wrappers

**Frontend — Gemini:**
- `frontend/app/(dashboard)/favorites/page.tsx` — favorites listing page
- `frontend/components/features/favorites/favorite-button.tsx` — optimistic toggle button
- Integrate FavoriteButton into existing property card and property detail page

## Non-Goals

- Sharing favorites with other users
- Favorites folders or tags
- Notifications on favorited listings
- Persistent database storage (in-memory store is sufficient, same pattern as F2/F3)

## Constraints

- All implementation must follow `.ai/conventions.md` and `.ai/orchestration.md`.
- Workers must implement only their assigned task.
- `status.json` is updated only by Claude Code orchestration.

## Dependencies

- F2-property-browsing (done) — PropertyRead schema and property endpoints required

## Required Env Vars

No new env vars.
