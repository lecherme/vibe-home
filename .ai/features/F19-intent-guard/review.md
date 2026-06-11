# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | `_is_property_search(query: str) -> bool` exists in [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:71). |
| A2 | PASS | Heuristics run before LLM fallback in [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:76); `complete()` is only reached after both heuristic loops. |
| A3 | PASS | `ai_search()` guards before `_parse_filters` in [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:526); non-search early return sets `items=[]`, `total=0`, `query_parsed=False`. |
| A4 | PASS | Backend container run: `_is_property_search("上海房价为什么涨") == False`. |
| A5 | PASS | Backend container run: `_is_property_search("最近股市怎么样") == False`. |
| A6 | PASS | Backend container run: `_is_property_search("3室2卫 预算300万") == True`. |
| A7 | PASS | Backend container run: `_is_property_search("嘉定有什么二手房") == True`. |
| A8 | PASS | Backend container run: `_is_property_search("2 bedrooms near subway") == True`. |
| A9 | PASS | Backend container run: `ai_search("最近股市怎么样", 1, 10)` returned `total=0`, `query_parsed=False`, and a non-empty redirect summary. A patched run with `_parse_filters` / retrieval / summary helpers forced to raise still returned early, confirming the pipeline was skipped. |
| A10 | PASS | `git diff -- backend/tests/test_eval.py backend/tests/eval_set.json` is empty. Replayed `backend/tests/eval_set.json` against current `_normalize_query` in the backend container: `30/30` passing. |
| A11 | PASS | Backend container run: `ai_search("2 bedrooms", 1, 10)` returned `total=29`, so the normal property-search path still produces results. |
| Heuristic Coverage | FAIL | Clear property-search phrasing is not fully covered by heuristics in [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:41). Instrumentation showed `_is_property_search("嘉定有什么二手房")` makes 1 `complete()` call, so this “clear signal” case depends on the LLM instead of the keyword pass. |
| Frontend Boundary | PASS | No frontend files were changed; business logic remains in backend service code. |
| API Types | PASS | Backend schemas were not changed, and existing frontend types in [search.ts](/home/lecherme/workspace/vibe-home/frontend/types/search.ts:1) still match [ai_search.py](/home/lecherme/workspace/vibe-home/backend/app/schemas/ai_search.py:1) and [search.py](/home/lecherme/workspace/vibe-home/backend/app/schemas/search.py:1). |
| `status.json` Ownership | PASS | `.ai/features/F19-intent-guard/status.json` is modified in the working tree, but the Activity Log attributes that T02 update to Claude, not Codex or Gemini. No evidence shows Codex/Gemini changed it. |

## Issues Found
- BLOCKER: Clear property-search inputs still fall through to the LLM classifier because the heuristic patterns in [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:41) are too narrow. In a patched verification run, `_is_property_search("嘉定有什么二手房")` issued 1 `complete()` call, and forcing `complete()` to return `false` made the function return `False`. The spec says location-as-filter and explicit property-search intent should be handled by the keyword pass, not delegated to the fallback model.
- WARNING: The spec’s example query `3室2卫 预算300万` returned `total=0` in the current backend container data. A11 still passed with another property-search query (`2 bedrooms`), but this example is not a reliable smoke test against the current dataset.

## Required Fixes
- Expand `_PROPERTY_SEARCH_PATTERNS` in [service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:41) so obviously property-oriented queries are classified by heuristics alone, at minimum location-first/property-type requests like `嘉定有什么二手房` and bare buy/rent intents such as `买房` / `租房`. Re-verify those inputs return `True` with zero `complete()` calls.

## Approved Items
- The intent guard is integrated at the correct entry point in `ai_search()`.
- Non-search queries now short-circuit with empty results and a redirect message.
- Protected eval files are unchanged, and the F16 deterministic eval still passes `30/30`.
- No frontend, schema, or LLM service files were modified for this feature.

