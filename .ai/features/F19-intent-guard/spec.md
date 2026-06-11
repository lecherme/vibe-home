# F19 — Intent Guard

## Goal

Before entering the search/relaxation pipeline, classify every incoming query as `property_search` or `non_search`. Non-search queries exit early with a polite redirect message and empty results — they never reach `_parse_filters`, embedding lookup, or LLM summary.

## Problem

Currently `ai_search()` treats every query as a property search. Queries like "上海房价为什么涨" or "最近股市怎么样" are passed through the full parsing and retrieval pipeline, producing nonsensical results and wasting LLM calls.

## Design

### Classification function

```python
def _is_property_search(query: str) -> bool
```

Two-pass approach:

1. **Keyword heuristics (primary):** if query contains strong property-search signals, return `True` immediately. If query contains strong non-search signals, return `False` immediately.
2. **LLM fallback:** for ambiguous queries that pass neither heuristic, ask the LLM to classify. The LLM receives a short system prompt and returns `true` or `false`.

Property-search signals include: explicit buy/rent intent, room counts, budget mentions, property types, location as a search parameter.

Non-search signals include: "为什么", "怎么", "是不是", "分析", "预测", "政策", standalone market/trend queries.

### Integration point

Called at the top of `ai_search()`, before `_parse_filters`:

```python
def ai_search(query: str, page: int, page_size: int) -> AiSearchResult:
    ...
    if not _is_property_search(query):
        return AiSearchResult(
            items=[],
            total=0,
            page=max(page, 1),
            page_size=min(max(page_size, 1), _SEARCH_MAX_PAGE_SIZE),
            parsed_filters=SearchFilters(),
            ai_summary="这个问题不是房源筛选，我可以帮你按预算、区域、户型、通勤等条件找房。",
            query_parsed=False,
        )
    ...
```

## Non-Goals

- No new fields added to `AiSearchResult` or `SearchFilters`
- No frontend changes
- No multi-intent classification (only binary: property_search vs non_search)
- No conversation history or context — classification is stateless per query

## Files in Scope

- `backend/app/services/ai_search/service.py` only
