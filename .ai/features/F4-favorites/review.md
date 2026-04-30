# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | `backend/app/schemas/favorite.py` exists and defines `FavoriteRead` / `FavoriteList`. |
| A2 | PASS | `backend/app/services/favorites/service.py` implements `add_favorite()`, `remove_favorite()`, `get_user_favorites()`, and `is_favorite()`. |
| A3 | PASS | `POST /api/v1/favorites/{property_id}` returns `201`; covered by `backend/tests/test_favorites.py:111-122` and verified with `backend/.venv/bin/python -m pytest backend/tests/test_favorites.py -q`. |
| A4 | PASS | Duplicate `POST` returns `409`; covered by `backend/tests/test_favorites.py:125-135`. |
| A5 | PASS | `DELETE /api/v1/favorites/{property_id}` returns `204`; covered by `backend/tests/test_favorites.py:138-149`. |
| A6 | PASS | `GET /api/v1/favorites` is user-scoped; covered by `backend/tests/test_favorites.py:152-170`. |
| A7 | PASS | All favorites endpoints return `401` unauthenticated; covered by `backend/tests/test_favorites.py:173-189`. |
| A8 | PASS | All favorites endpoints return `403` for admin role; covered by `backend/tests/test_favorites.py:192-208`. |
| A9 | PASS | `frontend/types/favorites.ts` exists with `Favorite` and `FavoriteList` interfaces. |
| A10 | PASS | `frontend/lib/api/favorites.ts` exists with `addFavorite()`, `removeFavorite()`, and `getFavorites()`. No extra `isFavorite()` API helper was added. |
| A11 | PASS | `frontend/app/(dashboard)/favorites/page.tsx` exists. |
| A12 | PASS | `frontend/components/features/favorites/favorite-button.tsx` exists. |
| A13 | PASS | `FavoriteButton` is rendered on the property card in `frontend/components/features/properties/PropertyCard.tsx:29-31`. |
| A14 | PASS | `FavoriteButton` is rendered on the property detail page in `frontend/app/(dashboard)/properties/[id]/page.tsx:95-97`. |
| A15 | FAIL | The button toggles optimistically, but the detail page still computes initial favorite state incorrectly. `FavoriteButton` snapshots `initialIsFavorited` once in `frontend/components/features/favorites/favorite-button.tsx:17` and never resyncs, while the parent resolves that prop asynchronously via `frontend/app/(dashboard)/properties/[id]/page.tsx:45-49`. Also, that lookup only inspects the first favorites page because `getFavorites()` defaults to `pageSize = 12` in `frontend/lib/api/favorites.ts:44-56`. Existing favorites can therefore render as unfavorited and stay wrong, leading to duplicate `409` responses instead of allowing unfavorite from the detail page. |
| A16 | PASS | Favorites UI components use `favoritesApi`; no direct `fetch()` or Supabase calls appear in the favorites UI files. |
| A17 | PASS | `backend/.venv/bin/python -m pytest backend/tests/test_favorites.py -q` passed: `13 passed in 0.31s`. |
| A18 | PASS | `frontend` TypeScript compile check passed: `npx tsc --noEmit` exited `0`. |

## Issues Found
- BLOCKER: `frontend/components/features/favorites/favorite-button.tsx:17` initializes local state from `initialIsFavorited` only once. On the detail page, `frontend/app/(dashboard)/properties/[id]/page.tsx:45-49` fetches favorite membership asynchronously after mount, so if the property request resolves first, an already-favorited listing renders with the wrong button state and never corrects itself.
- BLOCKER: `frontend/app/(dashboard)/properties/[id]/page.tsx:45-49` derives favorite membership by calling `favoritesApi.getFavorites()` with its default pagination, and `frontend/lib/api/favorites.ts:44-56` limits that to the first 12 favorites. Any older saved property beyond that first page is treated as “not favorited” on the detail page.
- WARNING: The detail page is carrying domain logic by loading the user’s favorites list and scanning it client-side for membership. That crosses the intended “UI-local state” boundary and is the reason the stale-state/pagination bug exists.
- WARNING: There is no frontend coverage for the already-favorited detail-page path or the `>12 favorites` case. The current verification is compile-only on the frontend, so this regression was not exercised.
- MINOR: `status.json` is currently modified, but the available evidence points to Claude-owned rerun orchestration only: the diff is T05 retry metadata and the activity log attributes the relevant entries to `"by": "claude"`.

## Required Fixes
- Fix the detail-page initial favorite state so it is correct before the button becomes interactive, or make `FavoriteButton` resync when `initialIsFavorited` changes.
- Remove the truncated first-page membership check on the detail page; the current-property favorite state must not depend on `getFavorites()` defaults.
- Add verification for an already-favorited property detail view, including a case where the property is not in the first page of favorites.

## Approved Items
- Backend schemas, service functions, router wiring, auth enforcement, and user scoping are implemented and validated by passing backend tests.
- Frontend API types are published under `frontend/types/`, and the typed favorites API wrapper exposes the required three functions.
- The favorites page includes loading, empty, and error states, and unfavoriting from that page removes the card from the list.
- No extra backend favorites status endpoint was added.
- No evidence was found that Codex or Gemini modified `status.json`; the current diff aligns with Claude-owned review rerun state.
