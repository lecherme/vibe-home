# F20 — Relaxation Layer

## Goal

When strict filter search returns zero or too few results, progressively relax soft constraints and re-run retrieval. Return the best available results with a summary that explains what was relaxed. Hard constraints are never touched.

## Problem

Currently if parsed filters are slightly too strict, `_resolve_result_ids` returns 0 or very few results and the user sees an empty or near-empty response with no explanation. One mismatched constraint can kill the entire search.

## Trigger conditions

Both modes only activate when `query_parsed=True`. When `query_parsed=False` (keyword fallback), relaxation is skipped entirely.

| Mode | Condition | Behaviour |
|------|-----------|-----------|
| **Rescue** | `strict_count == 0` | Replace strict results with relaxed results |
| **Supplement** | `0 < strict_count < _RELAX_SUPPLEMENT_THRESHOLD` | Keep strict results first, append unique relaxed results |

`_RELAX_SUPPLEMENT_THRESHOLD = 3`

## Hard vs soft constraints

**Hard — never relaxed:** `max_price`, `min_price`, `status`

**Soft — relaxed in this order:**
1. `bedrooms_min` — reduce by 1 (if > 1); remove entirely if already 1
2. `bathrooms_min` — reduce by 1 (if > 1); remove entirely if already 1
3. `location` — remove entirely

Maximum 3 relaxation steps. If strict count is still 0 after all steps, return empty results with a summary explaining that no close matches were found even after relaxing soft constraints.

## Implementation

### New function: `_relax_filters`

```python
def _relax_filters(filters: SearchFilters) -> tuple[SearchFilters, str] | None:
```

Applies exactly one relaxation step and returns `(relaxed_filters, human_readable_description)`, or `None` if no soft constraint remains to relax.

### New function: `_apply_relaxation`

```python
def _apply_relaxation(
    query: str,
    filters: SearchFilters,
    query_parsed: bool,
) -> tuple[list[str], SearchFilters, list[str]]:
```

Loops over `_relax_filters` steps (max 3). After each step, calls `_resolve_result_ids` with the relaxed filters. Stops when `len(result_ids) >= _RELAX_SUPPLEMENT_THRESHOLD` or no more steps remain. Returns `(result_ids, final_filters, relaxed_conditions)` where `result_ids` and `final_filters` reflect the last relaxation step that produced results (or the last step tried if still empty).

### Integration in `ai_search()`

```python
result_ids = _resolve_result_ids(query, parsed_filters, query_parsed=query_parsed)
relaxed_conditions: list[str] = []

if query_parsed:
    strict_count = len(result_ids)
    if strict_count == 0:
        result_ids, parsed_filters, relaxed_conditions = _apply_relaxation(
            query, parsed_filters, query_parsed
        )
    elif strict_count < _RELAX_SUPPLEMENT_THRESHOLD:
        relaxed_ids, _, relaxed_conditions = _apply_relaxation(
            query, parsed_filters, query_parsed
        )
        seen = set(result_ids)
        for rid in relaxed_ids:
            if rid not in seen:
                result_ids.append(rid)
                seen.add(rid)
```

Both paths use `_apply_relaxation`'s return values. Rescue replaces `result_ids` and `parsed_filters`. Supplement merges (strict first, relaxed appended, deduplicated).

### `_generate_summary` update

Add `relaxed_conditions: list[str] = []` parameter. When non-empty, include the list in the prompt so the LLM can explain what was relaxed in the summary.

## Summary message guidance (in LLM prompt)

- Rescue: tell LLM that strict filters returned 0 results and list what was relaxed
- Supplement: tell LLM that strict results were few and relaxed results were appended
- No match after all steps: LLM explains no close matches were found even after relaxing soft constraints

## Non-Goals

- No new fields on `AiSearchResult` or `SearchFilters`
- No frontend changes
- No relaxation of `max_price`, `min_price`, or `status`
- No relaxation when `query_parsed=False`
- No relaxation of `bedrooms_max` or `bathrooms_max`

## Files in Scope

- `backend/app/services/ai_search/service.py` only
