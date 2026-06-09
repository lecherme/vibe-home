# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | `backend/app/schemas/search.py:7-15` contains `bedrooms_min`, `bedrooms_max`, `bathrooms_min`, `bathrooms_max`; legacy `bedrooms`/`bathrooms` fields are gone. |
| A2 | PASS | `backend/app/services/search/service.py:32-54` applies `>=` semantics for `_min` and `<=` semantics for `_max` by skipping `< min` and `> max`. |
| A3 | PASS | `_normalize_query` exists at `backend/app/services/ai_search/service.py:48-141` and implements `万/w` expansion, price min/max extraction, and bedroom/bathroom comparator handling including `more than -> +1` and `less than -> -1`. |
| A4 | PASS | `_parse_filters` calls `_normalize_query` first at `backend/app/services/ai_search/service.py:183-190`, builds `deterministic_filters`, and merges them over LLM output at `:209`. |
| A5 | PASS | The LLM prompt at `backend/app/services/ai_search/service.py:193-200` only asks for `location`, `status`, and `remainder`, and explicitly forbids price/bedroom/bathroom extraction. |
| A6 | PASS | `backend/tests/eval_set.json` contains 30 queries. Replaying current `_normalize_query` against that eval set returned `30/30` passes (100%). `backend/tests/test_eval.py:14-45` enforces `>=25` cases and `>=80%` pass rate. |
| A7 | PASS | The regular search endpoint in `backend/app/api/v1/properties/router.py:47-72` now accepts `bedrooms_min`, `bedrooms_max`, `bathrooms_min`, `bathrooms_max` and no longer accepts legacy aliases. |
| A8 | PASS | `docker compose exec backend python -c "import app.main; print('OK')"` returned `OK`. |
| A9 | PASS | `frontend/types/search.ts:3-11` matches the backend schema and no longer exposes `bedrooms`/`bathrooms` on `SearchFilters`. |
| A10 | PASS | `frontend/components/features/search/ai-parsed-filters-card.tsx:42-79` renders `>= X Beds`, `<= X Beds`, `X–Y Beds`, and the same bathroom variants. |
| A11 | PASS | The filter UI and API wiring use the renamed fields: `frontend/lib/api/properties.ts:84-126`, `frontend/components/features/search/filter-panel.tsx:125-202`, and `frontend/app/(dashboard)/search/page.tsx:32-39,93-119`. |
| A12 | PASS | `cd frontend && npx tsc --noEmit` exited `0`. |
| A13 | PASS | Inferred from code: `_normalize_query` maps `"2个卧室以上 预算2000万"` to `bedrooms_min=2`, `max_price=20000000`, and the chip renderer shows `>= 2 Beds` plus `< $20000000`. Not manually exercised. |
| A14 | PASS | Inferred from code: `_normalize_query` maps `"more than 2 bedrooms under 8000000 hkd"` to `bedrooms_min=3`, `max_price=8000000`, and the chip renderer shows `>= 3 Beds` plus `< $8000000`. Not manually exercised. |
| A15 | PASS | Inferred from code: `_normalize_query` maps `"less than 4 bedrooms"` to `bedrooms_max=3`, and the chip renderer shows `<= 3 Beds`. Not manually exercised. |
| A16 | PASS | Inferred from code: filter search still deserializes URL params, rebuilds them, and calls the regular search API with the renamed fields. Not manually exercised. |

## Issues Found
- BLOCKER: `backend/tests/test_search.py:287-290` is modified even though it is outside T01’s authorized file set, is not covered by Fix Loop Authorized Files, and has no Activity Log revert entry. The change is logically correct, but it is still a scope/boundary violation.
- WARNING: The documented backend verification command `docker compose exec backend python -m pytest tests/test_eval.py -v` still fails in the current compose setup with `ERROR: file or directory not found: tests/test_eval.py` because the backend container does not mount the repo `backend/tests` directory.
- WARNING: Regression coverage for regular search is thin. `backend/tests/test_search.py` only updates the existing min-bedroom case; there is still no automated coverage for `bedrooms_max`, `bathrooms_min`, `bathrooms_max`, or the `/api/v1/properties/search` query-param wiring.

## Required Fixes
- Revert `backend/tests/test_search.py` or formally authorize that file in scope before acceptance.

## Approved Items
- `status.json` shows Claude-owned workflow bookkeeping only; the current rerun entries in the Activity Log are recorded with `"by": "claude"`, and I found no evidence of a Codex or Gemini edit to that file.
- The backend schema, AI parser, and regular search API now share the same `SearchFilters` shape using `bedrooms_min/max` and `bathrooms_min/max`.
- Deterministic numeric parsing remains in backend service code; no property-search business logic was moved into frontend components.
- The published frontend API types in `frontend/types/search.ts` match the backend schema and are used by the frontend search client/UI.
