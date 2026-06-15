# F23 Acceptance Criteria

## Verification method note

A3–A9 involve LLM output. To avoid model variability causing false failures:

- **A3–A7** may be verified with a patched/fake LLM response that returns the expected JSON; this isolates merge and routing logic from model behaviour.
- **A8–A9** must be verified with a patched LLM response returning out-of-range values, to confirm the validation drop logic works correctly.
- Alternatively, real LLM calls may be used for A3–A7 as a smoke check, but a deterministic pass via fake LLM response is also acceptable and preferred for stability.

## LLM output extension

| ID | Criterion |
|----|-----------|
| A1 | `_parse_filters` system prompt lists `subway_distance_max` and `built_year_min` as allowed output keys |
| A2 | The prompt provides the computed `current_utc_year - 10` as a concrete 4-digit year for "新楼/次新房"; no relative arithmetic is expected from the LLM |

## Vocabulary recognition (verified via patched or real LLM)

| ID | Criterion |
|----|-----------|
| A3 | When LLM returns `{"subway_distance_max": 500}` for query "近地铁", the merged `SearchFilters` has `subway_distance_max=500` |
| A4 | When LLM returns `{"built_year_min": <current_utc_year - 10>}` for query "新楼", the merged `SearchFilters` has the correct `built_year_min` |
| A5 | When LLM returns `{"built_year_min": <current_utc_year - 10>}` for query "次新房", the merged `SearchFilters` has the correct `built_year_min` |

## Merge priority

| ID | Criterion |
|----|-----------|
| A6 | When deterministic parsing already set `subway_distance_max=300` and LLM returns `subway_distance_max=500`, the final value is 300 (deterministic wins) |
| A7 | `_parse_filters("100平以上近地铁")` with LLM returning `{"subway_distance_max": 500}` → result has both `area_min=100` (deterministic) and `subway_distance_max=500` (LLM) |

## Validation (verified via patched LLM returning invalid values)

| ID | Criterion |
|----|-----------|
| A8 | When LLM returns `subway_distance_max=99999`, the value is dropped and not merged into `SearchFilters` |
| A9 | When LLM returns `built_year_min=1800`, the value is dropped and not merged into `SearchFilters` |

## Non-regression

| ID | Criterion |
|----|-----------|
| A10 | `_relax_filters`, `_apply_relaxation`, `_is_property_search`, `_resolve_result_ids`, `_generate_summary` are unchanged |
| A11 | `backend/tests/eval_set.json` and `backend/tests/test_eval.py` unchanged |
| A12 | F16 eval passes 30/30 after F23 changes |
| A13 | `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exits 0 |
