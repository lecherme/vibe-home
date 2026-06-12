# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | `_relax_filters` exists in [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:463), applies one ordered step per call (`bedrooms_min` → `bathrooms_min` → `location`), and returns `None` when exhausted. |
| A2 | PASS | `_apply_relaxation` exists in [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:497), loops up to `_MAX_RELAXATION_STEPS = 3`, calls `_resolve_result_ids` after each step, stops at threshold/exhaustion, and returns last successful or last tried state. |
| A3 | PASS | `_generate_summary(..., relaxed_conditions: list[str] = [])` is present in [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:540) and includes relaxation guidance in the prompt when non-empty. |
| A4 | PASS | `_relax_filters(SearchFilters(max_price=5000000)) -> None` in direct container execution; hard constraints were not modified. |
| A5 | PASS | Direct container checks matched all required rows for `_relax_filters`; no mismatches found. |
| A6 | PASS | Using `F_zero = SearchFilters(location='嘉定')`, strict count was `0`; `_apply_relaxation('test', F_zero, True)` returned non-empty `relaxed_conditions` and attempted rescue successfully. |
| A7 | PASS | `ai_search` rescue integration works when forced onto `F_zero`; returned non-empty, non-redirect summary and non-zero total. Verified with service-level monkeypatching to isolate relaxation flow from LLM/env dependencies. |
| A8 | PASS | Using `F_few = SearchFilters(location='Kennedy Town')`, strict count was `2`; `_apply_relaxation('test', F_few, True)` returned `39` ids and non-empty `relaxed_conditions`. |
| A9 | PASS | `ai_search` supplement integration works when forced onto `F_few`; returned `total > 0` and non-empty summary. Verified with service-level monkeypatching to isolate relaxation flow from LLM/env dependencies. |
| A10 | FAIL | `_apply_relaxation('test', SearchFilters(bedrooms_min=2), False)` returned a relaxed filter result and descriptions instead of `([], F_any, [])`. There is no early return for `query_parsed=False` in [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:497). |
| A11 | PASS | For parsed `bedrooms_min=2`, result count was `29 >= 3`; by inspection the supplement branch only runs when `strict_count < 3`, so no relaxation is triggered for this case. |
| A12 | PASS | `backend/tests/test_eval.py` and `backend/tests/eval_set.json` are unchanged by diff. `test_eval.py` exercises `_normalize_query`, which was not modified, so F16 eval impact is unchanged by inspection. |
| Frontend/business-logic boundary | PASS | No frontend files changed; relaxation logic remains in backend service only. |
| `status.json` not modified by Codex/Gemini | PASS | `status.json` is dirty in the worktree, but the Activity Log attributes the T02 update to `claude`; no evidence shows Codex or Gemini modified it. |
| API types published to `frontend/types/` | PASS | No backend schema/API shape changed; existing `frontend/types/search.ts` still matches backend `SearchFilters` and `AiSearchResult`. |

## Issues Found
- BLOCKER: `_apply_relaxation` violates the no-relaxation helper contract for `query_parsed=False`; it still relaxes soft constraints and can return keyword-search matches. Repro: `_apply_relaxation('test', SearchFilters(bedrooms_min=2), False)` returned non-empty results and relaxation notes. See [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:497).
- WARNING: No automated test coverage was added for `_relax_filters` / `_apply_relaxation`; A5 was only verifiable through manual execution during review, so this change remains regression-prone.

## Required Fixes
- Add an immediate guard at the top of `_apply_relaxation` to return `([], filters, [])` when `query_parsed` is `False`.

## Approved Items
- `_RELAX_SUPPLEMENT_THRESHOLD` and `_MAX_RELAXATION_STEPS` were added and used consistently.
- `_relax_filters` preserves hard constraints and follows the required relaxation order.
- Rescue integration replaces `result_ids` and `parsed_filters` as specified.
- Supplement integration preserves strict results first and appends unique relaxed ids.
- `_generate_summary` receives relaxation context and can explain rescue/supplement behavior.
- `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exited `0`.
- No backend schema, frontend type, eval file, or frontend component changes were introduced by the feature implementation.
