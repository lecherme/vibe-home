# Favorites — Acceptance Criteria

T05 (Codex review) verifies every criterion below and writes `review.md`.
T06 (Claude acceptance) reads `review.md` and writes `final-report.md`.

---

## Criteria

| # | Criterion | Check |
|---|-----------|-------|
| A1 | FavoriteRead and FavoriteList Pydantic schemas exist in backend/app/schemas/favorite.py | File exists check |
| A2 | FavoritesService implements add_favorite(), remove_favorite(), get_user_favorites(), is_favorite() | Backend code review |
| A3 | POST /api/v1/favorites/{property_id} returns 201 on success | Backend test |
| A4 | POST /api/v1/favorites/{property_id} returns 409 on duplicate | Backend test |
| A5 | DELETE /api/v1/favorites/{property_id} returns 204 on success | Backend test |
| A6 | GET /api/v1/favorites returns only the current user's favorited properties (user-scoped) | Backend test |
| A7 | All favorites endpoints return 401 for unauthenticated requests | Backend test |
| A8 | All favorites endpoints return 403 for admin role | Backend test |
| A9 | frontend/types/favorites.ts exists with Favorite, FavoriteList, and FavoriteStatus interfaces | File exists check |
| A10 | frontend/lib/api/favorites.ts exists with addFavorite(), removeFavorite(), getFavorites(), isFavorite() | File exists check |
| A11 | Favorites page exists at frontend/app/(dashboard)/favorites/page.tsx | File exists check |
| A12 | FavoriteButton component exists in frontend/components/features/favorites/favorite-button.tsx | File exists check |
| A13 | FavoriteButton is rendered on property card (property-card.tsx) | Frontend code review |
| A14 | FavoriteButton is rendered on property detail page | Frontend code review |
| A15 | FavoriteButton uses optimistic update — UI state changes before server confirms | Frontend code review |
| A16 | No direct fetch() or Supabase calls in favorites UI components | Frontend code review |
| A17 | All backend tests in test_favorites.py pass | Test execution |
| A18 | Frontend TypeScript compiles without errors | Build check |
| A19 | GET /api/v1/favorites/{property_id} returns {"is_favorite": bool}; returns 401 unauthenticated, 403 for admin | Backend test |

## Review and Acceptance

If review verdict is FAIL, Claude does NOT proceed directly to T06 acceptance.
Claude must:
1. Write `last_review_failure` to `status.json` with fix_path, failed_criteria, and fix_instructions.
2. Choose fix_path: task_retry, direct_fixup, or review_rerun.
3. Apply the fix and re-run review before acceptance.

## Rejection Conditions

- Any task modifies files outside its ownership boundary.
- Any worker modifies `status.json`.
- Any required artifact is missing or malformed.
- Favorites are visible across users (A6 failed).
- Admin can access favorites endpoints (A8 failed).
