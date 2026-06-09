# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | FAIL | `SearchFilters` has the new min/max fields, but legacy `bedrooms`/`bathrooms` are still accepted via aliases in [backend/app/schemas/search.py](/home/lecherme/workspace/vibe-home/backend/app/schemas/search.py:11) and fallback normalization in [backend/app/services/ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:171). |
| A2 | PASS | `search()` applies `< bedrooms_min`, `> bedrooms_max`, `< bathrooms_min`, and `> bathrooms_max` correctly in [backend/app/services/search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/search/service.py:32). |
| A3 | PASS | `_normalize_query()` exists and deterministically handles `万/w`, budget/price bounds, and room comparator semantics in [backend/app/services/ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:48). |
| A4 | PASS | `_parse_filters()` calls `_normalize_query()` first and merges deterministic fields over LLM output in [backend/app/services/ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:179). |
| A5 | PASS | The LLM prompt only asks for `location`, `status`, and `remainder`, and explicitly says not to infer price/bed/bath fields in [backend/app/services/ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:193). |
| A6 | PASS | [backend/tests/eval_set.json](/home/lecherme/workspace/vibe-home/backend/tests/eval_set.json:1) contains 30 queries, and the build artifact records equivalent in-container eval passing 30/30. |
| A7 | FAIL | The renamed params were added, but the old ambiguous API params still exist as hidden inputs in [backend/app/api/v1/properties/router.py](/home/lecherme/workspace/vibe-home/backend/app/api/v1/properties/router.py:52), so the rename is not complete. |
| A8 | PASS | `docker compose exec backend python -c "import app.main; print('OK')"` passed. |
| A9 | PASS | Frontend `SearchFilters` uses only `bedrooms_min/max` and `bathrooms_min/max` in [frontend/types/search.ts](/home/lecherme/workspace/vibe-home/frontend/types/search.ts:3). |
| A10 | FAIL | `AiParsedFiltersCard` renders `≥` / `≤` instead of required `>=` / `<=` in [frontend/components/features/search/ai-parsed-filters-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/ai-parsed-filters-card.tsx:42). |
| A11 | PASS | Filter search wiring uses the new field names in [frontend/lib/api/properties.ts](/home/lecherme/workspace/vibe-home/frontend/lib/api/properties.ts:84) and [frontend/app/(dashboard)/search/page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:32). |
| A12 | PASS | `cd frontend && npx tsc --noEmit` exited 0. |
| A13 | FAIL | Backend normalization produces `bedrooms_min=2` and `max_price=20000000`, but the chip would render `≥ 2 Beds`, not required `>= 2 Beds`, due to [frontend/components/features/search/ai-parsed-filters-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/ai-parsed-filters-card.tsx:50). |
| A14 | FAIL | Backend normalization produces `bedrooms_min=3` and `max_price=8000000`, but the chip would render `≥ 3 Beds`, not required `>= 3 Beds`, due to [frontend/components/features/search/ai-parsed-filters-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/ai-parsed-filters-card.tsx:50). |
| A15 | FAIL | Backend normalization produces `bedrooms_max=3`, but the chip would render `≤ 3 Beds`, not required `<= 3 Beds`, due to [frontend/components/features/search/ai-parsed-filters-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/ai-parsed-filters-card.tsx:52). |
| A16 | PASS | By code inspection, filter search still uses the updated params consistently and compiles cleanly; no direct regression was found in [frontend/app/(dashboard)/search/page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:57). |

## Issues Found
- BLOCKER: Legacy ambiguous `bedrooms`/`bathrooms` inputs remain accepted in production code via schema aliases, AI normalization fallback, and hidden router params in [backend/app/schemas/search.py](/home/lecherme/workspace/vibe-home/backend/app/schemas/search.py:11), [backend/app/services/ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:171), and [backend/app/api/v1/properties/router.py](/home/lecherme/workspace/vibe-home/backend/app/api/v1/properties/router.py:56).
- BLOCKER: AI parsed filter chips do not match the required output format because they render Unicode `≥` / `≤` instead of literal `>=` / `<=` in [frontend/components/features/search/ai-parsed-filters-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/ai-parsed-filters-card.tsx:50).
- WARNING: Backend regression coverage still depends on the deprecated alias: [backend/tests/test_search.py](/home/lecherme/workspace/vibe-home/backend/tests/test_search.py:287) uses `SearchFilters(bedrooms=5)`, and there are no direct tests for `bedrooms_max`, `bathrooms_min/max`, or renamed endpoint params.
- MINOR: The exact documented container command `python -m pytest tests/test_eval.py` is not runnable as written in this environment because that path is not mounted in the backend container; verification currently relies on equivalent in-container execution instead.

## Required Fixes
- Remove legacy `bedrooms`/`bathrooms` acceptance from the backend schema, normalization layer, router, and tests so only `bedrooms_min/max` and `bathrooms_min/max` remain in the runtime contract.
- Update `AiParsedFiltersCard` to render the required comparator strings exactly: `>= X Beds`, `<= X Beds`, `>= X Baths`, `<= X Baths`.

## Approved Items
- `search()` correctly enforces min/max bedroom and bathroom bounds.
- `_normalize_query()` is deterministic and correctly parses the required price and comparator patterns.
- `_parse_filters()` normalizes before the LLM call and keeps numeric extraction out of the prompt.
- API types are published in [frontend/types/search.ts](/home/lecherme/workspace/vibe-home/frontend/types/search.ts:3) and used by the frontend.
- `status.json` is modified in the working tree, but its embedded activity log attributes those lifecycle edits to `claude`, not Codex or Gemini.
- Backend import verification passed, and frontend TypeScript verification passed.
