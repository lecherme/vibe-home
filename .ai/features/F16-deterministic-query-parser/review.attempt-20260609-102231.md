# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | `SearchFilters` contains only `bedrooms_min/max` and `bathrooms_min/max` in [search.py](/home/lecherme/workspace/vibe-home/backend/app/schemas/search.py:7). |
| A2 | PASS | `search()` enforces `< min` and `> max` skips for bedrooms and bathrooms in [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/search/service.py:33). |
| A3 | PASS | `_normalize_query()` implements deterministic `万/w` expansion, price bounds, and room comparator handling in [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:48). |
| A4 | PASS | `_parse_filters()` calls `_normalize_query()` first and merges deterministic fields over LLM output in [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:179). |
| A5 | PASS | The LLM prompt only asks for `location`, `status`, and `remainder`, and explicitly excludes price/bed/bath extraction in [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:193). |
| A6 | PASS | [eval_set.json](/home/lecherme/workspace/vibe-home/backend/tests/eval_set.json:1) has 30 queries, and [test_eval.py](/home/lecherme/workspace/vibe-home/backend/tests/test_eval.py:12) enforces `>=25` cases and `>=80%` pass rate. The recorded build evidence states equivalent in-container eval passed `30/30`. |
| A7 | PASS | Regular search now uses `bedrooms_min`, `bedrooms_max`, `bathrooms_min`, and `bathrooms_max` in [router.py](/home/lecherme/workspace/vibe-home/backend/app/api/v1/properties/router.py:47). |
| A8 | PASS | `docker compose exec backend python -c "import app.main; print('OK')"` returned `OK`. |
| A9 | PASS | Frontend `SearchFilters` matches the backend schema in [search.ts](/home/lecherme/workspace/vibe-home/frontend/types/search.ts:3). |
| A10 | FAIL | When both bounds are present and equal, `AiParsedFiltersCard` renders `X Beds` / `X Baths` instead of the required `X–Y Beds` / `X–Y Baths` in [ai-parsed-filters-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/ai-parsed-filters-card.tsx:44). |
| A11 | PASS | Frontend filter wiring uses the renamed fields in [properties.ts](/home/lecherme/workspace/vibe-home/frontend/lib/api/properties.ts:84), [filter-panel.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/filter-panel.tsx:127), and [page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:35). |
| A12 | PASS | `docker compose exec frontend npx tsc --noEmit` exited `0`. |
| A13 | PASS | By code path, `"2个卧室以上 预算2000万"` normalizes to `bedrooms_min=2` and `max_price=20000000`, and the chips render `>= 2 Beds` plus `< $20000000`. Not manually exercised. |
| A14 | PASS | By code path, `"more than 2 bedrooms under 8000000 hkd"` normalizes to `bedrooms_min=3` and `max_price=8000000`, and the chips render `>= 3 Beds` plus `< $8000000`. Not manually exercised. |
| A15 | PASS | By code path, `"less than 4 bedrooms"` normalizes to `bedrooms_max=3`, and the chip renders `<= 3 Beds`. Not manually exercised. |
| A16 | PASS | Filter search still parses URL state and calls the regular search API with the renamed fields in [page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:87). Not manually exercised. |

## Issues Found
- BLOCKER: `AiParsedFiltersCard` violates A10 for equal min/max bounds by collapsing to `X Beds` / `X Baths` instead of always rendering the required range form when both bounds are present in [ai-parsed-filters-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/ai-parsed-filters-card.tsx:44).
- WARNING: The documented backend verification command `docker compose exec backend python -m pytest tests/test_eval.py -v` still fails in this compose setup because `/app/tests` is not mounted; verification currently depends on equivalent recorded in-container eval evidence rather than the exact command.
- WARNING: Regression coverage is still light for the new upper-bound fields and router params; [test_search.py](/home/lecherme/workspace/vibe-home/backend/tests/test_search.py:286) covers `bedrooms_min`, but there is no direct automated coverage for `bedrooms_max`, `bathrooms_min/max`, or endpoint serialization of those params.

## Required Fixes
- Update `AiParsedFiltersCard` so that when both `bedrooms_min` and `bedrooms_max` are present it always renders `X–Y Beds`, and when both `bathrooms_min` and `bathrooms_max` are present it always renders `X–Y Baths`, even when `X === Y`.

## Approved Items
- The backend schema, regular search service, AI parser, and frontend types are aligned on `bedrooms_min/max` and `bathrooms_min/max`.
- Deterministic parsing remains in backend service code; no property-search parsing logic was moved into frontend components.
- API types are published in [search.ts](/home/lecherme/workspace/vibe-home/frontend/types/search.ts:3).
- `status.json` is modified in the worktree, but its activity log attributes those edits to `claude`; I found no evidence of Codex or Gemini modifying it.
- Backend import verification and frontend TypeScript verification both passed.
