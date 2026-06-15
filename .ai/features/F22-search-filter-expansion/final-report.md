# F22 Final Report

## Disposition: ACCEPTED

## Criteria Results

| ID | Criterion | Result | Notes |
|----|-----------|--------|-------|
| A1 | `SearchFilters` exposes four new optional int fields | PASS | `search.py:7` |
| A2 | Frontend `SearchFilters` mirrors matching optional fields | PASS | `search.ts:3` |
| A3 | `search()` filters by `area_min` | PASS | `search/service.py:32` |
| A4 | `search()` filters by `area_max` | PASS | `search/service.py:35` |
| A5 | `search()` filters by `built_year_min`; excludes `built_year=None` | PASS | `search/service.py:62` |
| A6 | `search()` filters by `subway_distance_max`; excludes `subway_distance_m=None` | PASS | `search/service.py:71` |
| A7 | `_parse_filters("100平以上")` → `area_min=100` | PASS | Verified in container |
| A8 | `_parse_filters("80到120平")` → `area_min=80, area_max=120` | PASS | Verified in container |
| A9 | `_parse_filters("2010年后")` → `built_year_min=2010` | PASS | Verified in container |
| A10 | `_parse_filters("房龄10年内")` → `built_year_min=current_utc_year - 10` | PASS | Returns 2016 on 2026-06-15; not hardcoded |
| A11 | `_parse_filters("地铁500米内")` → `subway_distance_max=500` | PASS | Verified in container |
| A12 | `_has_filters(SearchFilters(area_min=80))` → `True` | PASS | Verified in container |
| A13 | `ai_search("100平以上", 1, 100).parsed_filters.area_min == 100` | PASS | Parse result reaches response |
| A14 | `ai_search("地铁500米内", 1, 100)` all results have `subway_distance_m <= 500` | PASS | 14 items returned, max_distance=480 |
| A15 | `_relax_filters` / `_apply_relaxation` unchanged | PASS | `git diff` shows no changes to those functions |
| A16 | `eval_set.json` and `test_eval.py` unchanged | PASS | `git diff` empty |
| A17 | F16 eval 30/30 unaffected | PASS | `pytest test_eval.py` — 30/30 confirmed |
| A18 | `import app.main` exits 0 | PASS | Verified in container |

## Summary

F22 is complete. Four new filter fields are wired end-to-end from deterministic parsing through to the search service:

- **`area_min` / `area_max`** — parsed from explicit sqm expressions; applied against `area_sqm`
- **`built_year_min`** — parsed from year expressions and relative age expressions using server UTC year; properties with `built_year=None` are excluded when filter is set
- **`subway_distance_max`** — parsed from explicit metre expressions; properties with `subway_distance_m=None` are excluded when filter is set

Known limitation: the `/search` REST endpoint does not yet expose the new query params. The service layer supports them fully; endpoint exposure is deferred.

No direct_fixup required. No relaxation changes. F16 eval unaffected.
