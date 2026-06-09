# F16 Acceptance Criteria

## Backend (T01)

| ID | Criterion |
|----|-----------|
| A1 | `SearchFilters` has `bedrooms_min`, `bedrooms_max`, `bathrooms_min`, `bathrooms_max`; no `bedrooms` or `bathrooms` fields |
| A2 | `search()` uses `bedrooms_min/max`, `bathrooms_min/max` with correct `>=` / `<=` semantics |
| A3 | `_normalize_query(query)` exists and handles: `万/w` price expansion, `以上/at least/or more` → `_min`, `more than/greater than` → `_min+1`, `以下/at most` → `_max`, `less than/fewer than` → `_max-1`, `预算/budget/under/below` → `max_price` |
| A4 | `_parse_filters` calls `_normalize_query` first; deterministic fields are not re-delegated to LLM |
| A5 | LLM prompt only requests `location`, `status`, unresolved fuzzy remainder |
| A6 | `eval_set.json` contains >= 25 queries; running eval script achieves >= 80% pass rate |
| A7 | Regular filter search API query params updated: `bedrooms` -> `bedrooms_min`, new `bedrooms_max`, `bathrooms_min`, `bathrooms_max` params |
| A8 | `python -c "import app.main"` exit 0 |

## Frontend (T02)

| ID | Criterion |
|----|-----------|
| A9 | `SearchFilters` type in `types/search.ts` updated: `bedrooms_min/max`, `bathrooms_min/max` (no `bedrooms`/`bathrooms`) |
| A10 | `AiParsedFiltersCard` renders: `bedrooms_min` as `>= X Beds`, `bedrooms_max` as `<= X Beds`, both as `X–Y Beds`; same for bathrooms |
| A11 | Filter search form uses updated field names (no runtime breakage) |
| A12 | `tsc --noEmit` exit 0 |

## Manual (T04 Claude)

| ID | Criterion |
|----|-----------|
| A13 | "2个卧室以上 预算2000万" → filter chips show `>= 2 Beds` + `< $20000000`, results present |
| A14 | "more than 2 bedrooms under 8000000 hkd" → chips show `>= 3 Beds` + `< $8000000` |
| A15 | "less than 4 bedrooms" → chips show `<= 3 Beds` |
| A16 | Filter Search tab still functions correctly (no regression) |
