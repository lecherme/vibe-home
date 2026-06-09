# F16 Final Acceptance Report

## Disposition: ACCEPTED

## Criteria Results

| ID | Result | Notes |
|----|--------|-------|
| A1 | PASS | `SearchFilters` has only `bedrooms_min/max`, `bathrooms_min/max`; legacy aliases removed |
| A2 | PASS | `search()` correctly applies `>=` / `<=` semantics for min/max bounds |
| A3 | PASS | `_normalize_query()` handles `万/w` expansion, price bounds, all comparison semantics |
| A4 | PASS | `_parse_filters` calls `_normalize_query` first; deterministic fields excluded from LLM |
| A5 | PASS | LLM prompt requests only `location`, `status`, `remainder` |
| A6 | PASS | 30 eval queries; 30/30 pass (100%) — exceeds 80% threshold |
| A7 | PASS | Router updated: `bedrooms_min/max`, `bathrooms_min/max`; legacy params removed |
| A8 | PASS | `import app.main` exit 0 |
| A9 | PASS | `frontend/types/search.ts` uses `bedrooms_min/max`, `bathrooms_min/max` only |
| A10 | PASS | Chips render `>= X Beds`, `<= X Beds`, `X–Y Beds`; same for bathrooms |
| A11 | PASS | Filter search form and API client use renamed fields; no regression |
| A12 | PASS | `tsc --noEmit` exit 0 |
| A13 | PASS | "2个卧室以上 预算2000万" → `bedrooms_min=2, max_price=20000000` — verified in container |
| A14 | PASS | "more than 2 bedrooms under 8000000 hkd" → `bedrooms_min=3, max_price=8000000` — verified in container |
| A15 | PASS | "less than 4 bedrooms" → `bedrooms_max=3` — verified in container |
| A16 | PASS | Filter Search compiles cleanly; wiring unchanged — no regression observed |

## Known Limitations

- `docker compose exec backend python -m pytest tests/test_eval.py -v` cannot run as written; backend container does not mount `backend/tests/`. Equivalent in-container eval ran 30/30. Environment constraint, not a code defect.
- Regression coverage for `bedrooms_max`, `bathrooms_min/max` in `test_search.py` is light. Acceptable for this feature scope.

## Summary

F16 shipped a deterministic pre-processing layer (`_normalize_query`) that extracts price, bedroom, and bathroom bounds before any LLM call. The renamed schema (`bedrooms_min/max`, `bathrooms_min/max`) is now consistent across backend schema, search service, AI search service, regular search router, frontend types, API client, and filter UI. All 16 acceptance criteria pass.
