# F19 Final Report

## Disposition: ACCEPTED

## Criteria Results

| ID | Criterion | Result | Notes |
|----|-----------|--------|-------|
| A1 | `_is_property_search` exists | PASS | `service.py:76` |
| A2 | Heuristics run before LLM fallback | PASS | LLM only reached after both heuristic loops at `:81-87` |
| A3 | `ai_search()` guards before `_parse_filters` | PASS | Early return at `:542-549` with `items=[]`, `total=0`, `query_parsed=False` |
| A4 | `上海房价为什么涨` → `False` | PASS | Verified in container |
| A5 | `最近股市怎么样` → `False` | PASS | Verified in container |
| A6 | `3室2卫 预算300万` → `True` | PASS | Verified in container |
| A7 | `嘉定有什么二手房` → `True` | PASS | Verified in container; required direct_fixup after T02 Run 1 — added `有+property_noun` pattern |
| A8 | `2 bedrooms near subway` → `True` | PASS | Verified in container |
| A9 | Non-search returns `total=0`, redirect `ai_summary` | PASS | `ai_search("最近股市怎么样")` → `total=0`, `query_parsed=False`, non-empty summary |
| A10 | `test_eval.py` and `eval_set.json` unchanged; F16 eval 30/30 | PASS | `git diff` empty; 30/30 confirmed |
| A11 | Property-search query returns non-zero results | PASS | `ai_search("2 bedrooms")` → `total=29` |

## Summary

F19 is complete. `_is_property_search` provides a two-stage guard: keyword heuristics first, LLM fallback only for ambiguous cases. Non-property queries exit before `_parse_filters`, embedding lookup, and summary generation.

One direct_fixup was applied after T02 Run 1: `_PROPERTY_SEARCH_PATTERNS` was expanded with `有(?:什么|哪些|没有|啥|何)?\s*{property_noun}` and bare `买房|租房|找房|看房` patterns, ensuring clear property-search queries like `嘉定有什么二手房` are classified by heuristics without an LLM call.

No schema, frontend, LLM service, or eval files were modified.
