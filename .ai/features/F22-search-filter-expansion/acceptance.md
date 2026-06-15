# F22 Acceptance Criteria

## Schema

| ID | Criterion |
|----|-----------|
| A1 | `backend/app/schemas/search.py` `SearchFilters` exposes `area_min`, `area_max`, `built_year_min`, `subway_distance_max` as optional integer fields with `None` default |
| A2 | `frontend/types/search.ts` `SearchFilters` interface declares matching optional fields |

## Search

| ID | Criterion |
|----|-----------|
| A3 | `search()` filters out properties where `area_sqm < area_min` when `area_min` is set |
| A4 | `search()` filters out properties where `area_sqm > area_max` when `area_max` is set |
| A5 | `search()` filters out properties where `built_year < built_year_min` when `built_year_min` is set; properties with `built_year=None` are also excluded |
| A6 | `search()` filters out properties where `subway_distance_m > subway_distance_max` when `subway_distance_max` is set; properties with `subway_distance_m=None` are also excluded |

## Parsing

| ID | Criterion |
|----|-----------|
| A7 | `_parse_filters("100平以上")` → `area_min=100` |
| A8 | `_parse_filters("80到120平")` → `area_min=80, area_max=120` |
| A9 | `_parse_filters("2010年后")` → `built_year_min=2010` |
| A10 | `_parse_filters("房龄10年内")` → `built_year_min=current_utc_year - 10`; must not hardcode the year |
| A11 | `_parse_filters("地铁500米内")` → `subway_distance_max=500` |
| A12 | `_has_filters(SearchFilters(area_min=80))` → `True` |

## End-to-end service

| ID | Criterion |
|----|-----------|
| A13 | `ai_search("100平以上", 1, 10).parsed_filters.area_min == 100` — parse result reaches the returned filters |
| A14 | `ai_search("地铁500米内", 1, 10)` — every property in the result set has `subway_distance_m <= 500` (or the result set is empty if no properties qualify) |

## Non-regression

| ID | Criterion |
|----|-----------|
| A15 | `_relax_filters` and `_apply_relaxation` behaviour unchanged — new fields are not relaxed |
| A16 | `backend/tests/eval_set.json` and `backend/tests/test_eval.py` unchanged |
| A17 | F16 eval passes 30/30 after F22 changes |
| A18 | `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exits 0 |
