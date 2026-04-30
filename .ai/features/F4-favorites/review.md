# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | `backend/app/schemas/favorite.py` exists and defines `FavoriteRead` and `FavoriteList`. |
| A2 | PASS | `backend/app/services/favorites/service.py` implements `add_favorite()`, `remove_favorite()`, `get_user_favorites()`, and `is_favorite()`. |
| A3 | PASS | `POST /api/v1/favorites/{property_id}` returns `201`; covered by `backend/tests/test_favorites.py:111-122`. |
| A4 | PASS | Duplicate `POST` returns `409`; covered by `backend/tests/test_favorites.py:125-135`. |
| A5 | PASS | `DELETE /api/v1/favorites/{property_id}` returns `204`; covered by `backend/tests/test_favorites.py:138-149`. |
| A6 | PASS | `GET /api/v1/favorites` is user-scoped; covered by `backend/tests/test_favorites.py:152-170`. |
| A7 | PASS | All favorites endpoints return `401` unauthenticated; covered by `backend/tests/test_favorites.py:173-189`. |
| A8 | PASS | All favorites endpoints return `403` for admin role; covered by `backend/tests/test_favorites.py:192-208`. |
| A9 | PASS | `frontend/types/favorites.ts` exists with `Favorite` and `FavoriteList` interfaces. |
| A10 | PASS | `frontend/lib/api/favorites.ts` exposes `addFavorite()`, `removeFavorite()`, and `getFavorites()`. No extra `isFavorite()` API wrapper was added. |
| A11 | PASS | `frontend/app/(dashboard)/favorites/page.tsx` exists. |
| A12 | PASS | `frontend/components/features/favorites/favorite-button.tsx` exists. |
| A13 | PASS | `FavoriteButton` is rendered on the property card in `frontend/components/features/properties/PropertyCard.tsx`. |
| A14 | PASS | `FavoriteButton` is rendered on the property detail page in `frontend/app/(dashboard)/properties/[id]/page.tsx:95-97`. |
| A15 | PASS | `FavoriteButton` updates local state before awaiting the API and reverts on error in `frontend/components/features/favorites/favorite-button.tsx:33-52`. |
| A16 | PASS | Favorites UI components use `favoritesApi`; no direct `fetch()` or Supabase calls appear in the UI components/pages. |
| A17 | PASS | `backend/.venv/bin/python -m pytest backend/tests/test_favorites.py -q` passed: `13 passed`. |
| A18 | PASS | `frontend` TypeScript compile check passed: `npx tsc --noEmit` exited `0`. |
| Boundary: frontend business logic stays out of UI components | FAIL | `frontend/app/(dashboard)/properties/[id]/page.tsx:45-49` calls `favoritesApi.getFavorites(1, 1000)` and scans the returned list client-side to derive favorite membership. That is business logic in the page component and relies on an arbitrary pagination cap. |
| Boundary: `status.json` ownership | PASS | Current `status.json` retry-state edits are Claude-attributed in the activity log / blame output; no evidence found that Codex or Gemini modified it. |

## Issues Found
- BLOCKER: `frontend/app/(dashboard)/properties/[id]/page.tsx:45-49` implements favorite-membership logic in the UI by fetching the favorites list and searching it client-side. This violates the T04 boundary against business logic in components.
- BLOCKER: The `getFavorites(1, 1000)` workaround in `frontend/app/(dashboard)/properties/[id]/page.tsx:45-49` is still incorrect for users with more than 1000 favorites. In that case, an already-favorited property can render as not favorited and the next toggle can fail with `409`.
- WARNING: `backend/tests/test_favorites.py` does not cover the 404 paths promised by T02 done conditions, such as `POST` for an unknown property or `DELETE` for a missing favorite.
- WARNING: Frontend verification is still compile-only. There is no regression coverage for the already-favorited detail-page path or for large favorites lists.

## Required Fixes
- Remove favorite-membership derivation from `frontend/app/(dashboard)/properties/[id]/page.tsx`; the detail page must not fetch the favorites list and compute membership in the component.
- Replace the `pageSize=1000` workaround with an approach that does not depend on paginated list scanning for initial detail-page state.

## Approved Items
- Backend schemas, service logic, router wiring, auth enforcement, and user scoping are implemented and verified by passing backend tests.
- Frontend favorites types are published under `frontend/types/`, and the typed API wrapper exposes the required three functions.
- `FavoriteButton` is integrated into both property card and property detail views, and the button itself uses optimistic local updates with rollback on failure.
- The favorites page includes loading, empty, and error states and removes cards locally when an item is unfavorited.
- No extra backend favorites status endpoint was added.
