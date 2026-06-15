# F23 Final Report

## Disposition: ACCEPTED

## Criteria Results

| ID | Criterion | Result | Notes |
|----|-----------|--------|-------|
| A1 | `_parse_filters` system prompt lists `subway_distance_max` and `built_year_min` as allowed output keys | PASS | Both keys in prompt at service.py:531-532 |
| A2 | Prompt provides computed `current_utc_year - 10` as concrete 4-digit year; LLM not asked to do year arithmetic | PASS | `recent_building_year_min = current_utc_year - 10` computed in Python; injected via f-string at service.py:536 |
| A3 | LLM returns `{"subway_distance_max": 500}` → `SearchFilters.subway_distance_max=500` | PASS | Verified with patched LLM; got 500 |
| A4 | LLM returns `{"built_year_min": current_utc_year-10}` for "新楼" → correct `built_year_min` | PASS | Verified with patched LLM; got 2016 (2026-06-15 UTC) |
| A5 | LLM returns `{"built_year_min": current_utc_year-10}` for "次新房" → correct `built_year_min` | PASS | Verified with patched LLM; got 2016 |
| A6 | Deterministic `subway_distance_max=300` wins over LLM `subway_distance_max=500` | PASS | "地铁300米内近地铁" → 300 retained |
| A7 | `_parse_filters("100平以上近地铁")` → `area_min=100` (deterministic) + `subway_distance_max=500` (LLM) | PASS | Both fields present with correct values |
| A8 | LLM returns `subway_distance_max=99999` → value dropped | PASS | Exact-value enforcement rejects it |
| A9 | LLM returns `built_year_min=1800` → value dropped | PASS | Exact-value enforcement rejects it |
| A10 | `_relax_filters`, `_apply_relaxation`, `_is_property_search`, `_resolve_result_ids`, `_generate_summary` unchanged | PASS | `git diff HEAD` shows no changes to any protected function |
| A11 | `backend/tests/eval_set.json` and `backend/tests/test_eval.py` unchanged | PASS | `git diff HEAD` empty for both files |
| A12 | F16 eval passes 30/30 after F23 changes | PASS | `bash tools/run_eval.sh` → 2 passed (eval coverage + threshold tests) |
| A13 | `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exits 0 | PASS | Output: "OK" |

## Summary

F23 extends the existing LLM call in `_parse_filters` with a fixed-vocabulary middle layer:

- **`subway_distance_max`**: LLM recognizes "近地铁", "靠近地铁", "地铁口", "near MTR" etc. and must return exactly `500`; any other value is dropped.
- **`built_year_min`**: LLM recognizes "新楼", "次新房", "次新楼", "newer building" etc. and must return exactly `current_utc_year - 10` (computed by Python and injected as a concrete year); any other value is dropped.
- Deterministic parsing results always take priority over LLM output for the same field.
- Exact-value enforcement (not just range validation) ensures the LLM cannot invent arbitrary in-range thresholds.

**direct_fixup applied during T02:** Initial implementation used range-only validation (50–5000 / 1900–current_year+1). Fixed to enforce exact predefined values (`==500` / `==recent_building_year_min`) before merge.

No schema, API, frontend, or eval set changes. F16 eval unaffected.
