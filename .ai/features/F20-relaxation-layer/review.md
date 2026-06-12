# Review

## Verdict
PASS

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | `_relax_filters()` exists at [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:463) and applies exactly one step per call in the required order: `bedrooms_min` → `bathrooms_min` → `location`; returns `None` when no soft constraint remains. |
| A2 | PASS | `_apply_relaxation()` exists at [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:497), loops up to `_MAX_RELAXATION_STEPS = 3`, calls `_resolve_result_ids()` after each step, stops at `_RELAX_SUPPLEMENT_THRESHOLD`, and returns `(result_ids, final_filters, relaxed_conditions)`. |
| A3 | PASS | `_generate_summary()` includes `relaxed_conditions: list[str] = []` in its signature at [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:542) and injects relaxation guidance into the LLM prompt when non-empty at [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:566). |
| A4 | PASS | `_relax_filters()` only edits `bedrooms_min`, `bathrooms_min`, or `location` at [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:463); direct execution confirmed `_relax_filters(SearchFilters(max_price=5000000)) -> None`. |
| A5 | PASS | Direct container execution matched all required rows: `3->2` bedrooms, `1->None` bedrooms, `2->1` bathrooms, `location->None`, empty filters -> `None`, and `max_price`-only -> `None`. |
| A6 | PASS | Using `F_zero = SearchFilters(bedrooms_min=6)`, strict count was `0`; `_apply_relaxation('6 bedrooms', F_zero, True)` returned 5 ids and non-empty relaxation notes. |
| A7 | PASS | With deterministic query `6 bedrooms`, `ai_search()` returned non-empty `ai_summary`, `query_parsed=True`, and did not return `_NON_SEARCH_REDIRECT_MESSAGE`; service behavior was exercised with external LLM/embedding calls stubbed. |
| A8 | PASS | Using `F_few = SearchFilters(bedrooms_min=5)`, strict count was `1`; `_apply_relaxation('5 bedrooms', F_few, True)` returned 5 ids and non-empty relaxation notes, so `len(relaxed_ids) >= len(strict_ids)`. |
| A9 | PASS | With deterministic query `5 bedrooms`, `ai_search()` returned `total=5` and non-empty `ai_summary`; external LLM/embedding calls were stubbed to isolate service logic. |
| A10 | PASS | The rerun fix is present at [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:502); direct execution confirmed `_apply_relaxation(..., False) == ([], F_any, [])`. |
| A11 | PASS | `ai_search('2 bedrooms', 1, 10)` returned `total=29` in execution. By inspection, relaxation only runs when `strict_count < 3` at [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:654), so no relaxation is triggered for this case. |
| A12 | PASS | `backend/tests/test_eval.py` and `backend/tests/eval_set.json` are unchanged in the worktree. A one-off backend container run passed the eval suite (`2 passed`), and direct eval-set verification remained `30/30`. |
| `status.json` not modified by Codex/Gemini | PASS | `.ai/features/F20-relaxation-layer/status.json` is dirty in the current worktree, but the Activity Log attributes the rerun state changes on 2026-06-12 to `claude`, not Codex or Gemini. |
| API types published to `frontend/types/` | PASS | No backend schema/API shape changed in [search.py](/home/lecherme/workspace/vibe-home/backend/app/schemas/search.py:7) or [ai_search.py](/home/lecherme/workspace/vibe-home/backend/app/schemas/ai_search.py:12); existing frontend types still match at [search.ts](/home/lecherme/workspace/vibe-home/frontend/types/search.ts:3). |
| No frontend business logic | PASS | No frontend files were changed; the feature remains entirely in the backend service layer. |

## Issues Found
- WARNING: No permanent automated tests were added for `_relax_filters()` / `_apply_relaxation()` / `ai_search()` relaxation branching. The behavior now passes review-time execution, but the coverage is not codified in `backend/tests/`.

## Required Fixes
- None.

## Approved Items
- `_RELAX_SUPPLEMENT_THRESHOLD` and `_MAX_RELAXATION_STEPS` are defined and used consistently.
- `_relax_filters()` preserves hard constraints and follows the required relaxation order.
- `_apply_relaxation()` now correctly skips all relaxation when `query_parsed=False`.
- `ai_search()` implements both rescue and supplement paths, with strict results preserved first in supplement mode.
- Summary generation receives explicit relaxation guidance so rescue/supplement outcomes can be explained to the user.
- Regression risk to F16 parsing is low and current evidence is good: eval files are unchanged and the eval suite still passes.
