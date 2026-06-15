# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | `_parse_filters` system prompt now allows `subway_distance_max` and `built_year_min` in `backend/app/services/ai_search/service.py:531-532`. |
| A2 | PASS | Backend computes `recent_building_year_min = current_utc_year - 10` in Python and injects the concrete year into the prompt at `backend/app/services/ai_search/service.py:428-431,536-537`. |
| A3 | PASS | Patched LLM response `{"subway_distance_max": 500}` for `近地铁` merged to `SearchFilters.subway_distance_max=500`. |
| A4 | PASS | Patched LLM response `{"built_year_min": <current_utc_year - 10>}` for `新楼` merged correctly. |
| A5 | PASS | Patched LLM response `{"built_year_min": <current_utc_year - 10>}` for `次新房` merged correctly. |
| A6 | PASS | With deterministic `地铁300米内` and LLM `{"subway_distance_max": 500}`, final value stayed `300`. |
| A7 | PASS | `_parse_filters("100平以上近地铁")` preserved deterministic `area_min=100` and merged LLM `subway_distance_max=500`. |
| A8 | PASS | Patched LLM response `{"subway_distance_max": 99999}` was dropped before merge. |
| A9 | PASS | Patched LLM response `{"built_year_min": 1800}` was dropped before merge. |
| A10 | PASS | `git diff HEAD^ HEAD -- backend/app/services/ai_search/service.py` shows only `_parse_filters` changes; protected functions are unchanged. |
| A11 | PASS | `backend/tests/eval_set.json` and `backend/tests/test_eval.py` are unchanged in `HEAD^..HEAD`. |
| A12 | PASS | Ran the F16 eval logic in the backend container against the current `backend/tests/eval_set.json`; result was `30/30` passing. |
| A13 | PASS | `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exited `0` and printed `OK`. |

## Issues Found
- BLOCKER: `backend/app/services/ai_search/service.py:564-578` only range-validates LLM `subway_distance_max` and `built_year_min`. It does not enforce the fixed mapping values required by the spec. With a patched LLM, `_parse_filters("近地铁")` accepted `{"subway_distance_max": 450}` and `_parse_filters("新楼")` accepted `{"built_year_min": 2010}`. That violates the requirement that these vocabulary terms map only to predefined values `500` and `<current_utc_year - 10>`.

## Required Fixes
- Enforce backend-side fixed mapping before merge: accept `subway_distance_max` only when the LLM returns `500`, and accept `built_year_min` only when the LLM returns `recent_building_year_min`; otherwise drop the values even if they are in the allowed numeric range.

## Approved Items
- Prompt extension for the two new output keys is implemented correctly.
- The concrete precomputed year is injected from Python; the LLM is not asked to do relative year arithmetic.
- Deterministic parsing still takes precedence over LLM output.
- Out-of-range LLM values are dropped correctly.
- No frontend files were changed, so no business logic was moved into frontend components.
- No schema/API changes were made, so no frontend type publication was required; `frontend/types/search.ts` is unchanged.
- No evidence shows Codex or Gemini modified `.ai/features/F23-llm-middle-layer/status.json`; the runtime activity log attributes the current T02 status update to Claude.
