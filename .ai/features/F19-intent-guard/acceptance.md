# F19 Acceptance Criteria

## Structural (A1–A3) — code inspection

| ID | Criterion |
|----|-----------|
| A1 | `_is_property_search(query: str) -> bool` exists in `service.py` |
| A2 | Keyword heuristic pass runs before LLM fallback — LLM is only called when heuristics produce no clear signal |
| A3 | `ai_search()` calls `_is_property_search` before `_parse_filters`; non-search path returns `AiSearchResult` with `items=[]`, `total=0`, `query_parsed=False` |

## Functional (A4–A9) — verified via `_is_property_search` and `ai_search` in container

| ID | Query | Expected |
|----|-------|----------|
| A4 | `上海房价为什么涨` | `_is_property_search` → `False` |
| A5 | `最近股市怎么样` | `_is_property_search` → `False` |
| A6 | `3室2卫 预算300万` | `_is_property_search` → `True` |
| A7 | `嘉定有什么二手房` | `_is_property_search` → `True` |
| A8 | `2 bedrooms near subway` | `_is_property_search` → `True` |
| A9 | Non-search query passed to `ai_search()` returns `total=0` and `ai_summary` contains redirect message (non-empty string) |

## Regression (A10–A11)

| ID | Criterion |
|----|-----------|
| A10 | `test_eval.py` and `eval_set.json` unchanged; F16 eval 30/30 unaffected |
| A11 | A property-search query (e.g. `3室2卫 预算300万`) passed to `ai_search()` returns non-zero results (no regression on normal search path) |
