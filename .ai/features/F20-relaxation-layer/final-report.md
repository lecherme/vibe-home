# F20 Final Report

## Disposition: ACCEPTED

## Criteria Results

| ID | Criterion | Result | Notes |
|----|-----------|--------|-------|
| A1 | `_relax_filters` exists, one step per call, returns `None` when exhausted | PASS | `service.py:463` |
| A2 | `_apply_relaxation` loops max 3 steps, calls `_resolve_result_ids` per step, returns `(result_ids, final_filters, relaxed_conditions)` | PASS | `service.py:497` |
| A3 | `_generate_summary` accepts `relaxed_conditions` param, includes in LLM prompt when non-empty | PASS | `service.py:540` |
| A4 | Hard constraints never modified; `_relax_filters(SearchFilters(max_price=5000000))` → `None` | PASS | Verified in container |
| A5 | `_relax_filters` unit tests: all 6 input/output rows pass | PASS | Verified in container |
| A6 | `_apply_relaxation("test", F_zero, True)` returns non-empty `relaxed_conditions` | PASS | `F_zero=SearchFilters(location="嘉定")`, strict_count=0, relaxation attempted |
| A7 | `ai_search` rescue path: non-empty `ai_summary`, not redirect message | PASS | Verified via T02 service-level monkeypatching |
| A8 | `_apply_relaxation("test", F_few, True)` returns `len(relaxed_ids) >= len(strict_ids)`, non-empty conditions | PASS | `F_few=SearchFilters(location="Kennedy Town")`, strict_count=2 |
| A9 | `ai_search` supplement path: `total > 0`, non-empty `ai_summary` | PASS | Verified via T02 |
| A10 | `_apply_relaxation("test", SearchFilters(bedrooms_min=2), False)` → `([], filters, [])` | PASS | Fixed via direct_fixup after T02 Run 1 |
| A11 | `_resolve_result_ids` with `bedrooms_min=2` returns 29 results (>= threshold 3); no relaxation triggered | PASS | Verified in container |
| A12 | `test_eval.py` and `eval_set.json` unchanged; F16 eval 30/30 unaffected | PASS | `git diff` empty |

## Summary

F20 is complete. The relaxation layer adds two recovery paths to `ai_search()`:

- **Rescue** (`strict_count == 0`): replaces strict results with progressively relaxed results
- **Supplement** (`0 < strict_count < 3`): keeps strict results first, appends unique relaxed results

Relaxation order: `bedrooms_min` → `bathrooms_min` → `location`. Hard constraints (`max_price`, `min_price`, `status`) are never touched. Maximum 3 steps. Skipped entirely when `query_parsed=False`.

One direct_fixup applied after T02 Run 1: added `query_parsed=False` early return guard to `_apply_relaxation`.

No schema, frontend, LLM service, or eval files modified.
