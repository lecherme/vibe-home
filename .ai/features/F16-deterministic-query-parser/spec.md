# F16 — Deterministic Query Parser for AI Search

## Background

F15 shipped a working AI search but with ~60% parse success rate on DeepSeek. Root causes:

1. **Schema ambiguity**: `bedrooms` and `bathrooms` field names imply exact match but backend applies `>=` semantics. No `_max` variant exists for upper-bound queries.
2. **Full LLM dependency for structured fields**: Price units, comparison words, and bedroom/bathroom counts are delegated to the LLM. These are deterministic and should not require a model.
3. **SearchFilters mismatch**: Regular filter search and AI search share `SearchFilters` but field naming makes semantics ambiguous.

## Goal

Raise AI search parse accuracy by making price/bedroom/bathroom extraction deterministic, renaming ambiguous fields, and keeping LLM responsible only for fuzzy fields.

## Scope

### In scope

- **Schema rename**: `bedrooms` -> `bedrooms_min` + `bedrooms_max`; `bathrooms` -> `bathrooms_min` + `bathrooms_max`
- **Normalization layer** `_normalize_query`: deterministic pre-processing before LLM call
  - Price unit: `2500w` / `2500万` -> `25000000`
  - Comparison semantics for integer fields (bedrooms / bathrooms):
    - `以上` / `at least` / `or more` / `or above` -> `_min = X` (>= X)
    - `more than` / `greater than` / `超过` -> `_min = X + 1` (> X)
    - `以下` / `at most` / `不超过` / `or below` -> `_max = X` (<= X)
    - `less than` / `fewer than` / `少于` -> `_max = X - 1` (< X)
  - Price bounds: `under` / `below` / `以内` -> `max_price = X` (inclusive for prices)
  - Budget keywords: `预算` / `budget` -> max_price hint
- **Search service**: use `bedrooms_min/max`, `bathrooms_min/max`
- **LLM prompt**: instruct model to output only `location`, `status`, unresolved fuzzy remainder; never re-extract price/bedroom/bathroom if already resolved
- **Shared semantics**: regular search and AI search use identical `SearchFilters`
- **Eval set**: 25 labeled queries in `eval_set.json`, pass threshold >= 80%

### Out of scope

- Auto-fallback budget widening
- `area_min/max`, `property_type`, `district`, `sort` expansion
- Frontend filter search form redesign

## Architecture

```
User NL query
      |
_normalize_query()  -- extracts: min_price, max_price, bedrooms_min/max, bathrooms_min/max
      |
remaining text (location, status, fuzzy)
      |
LLM json_mode=True  -- only: location, status, unresolved fuzzy remainder
      |
merge (deterministic values take priority over LLM)
      |
SearchFilters -> search() + semantic_search()
```

## SearchFilters target schema

```python
class SearchFilters(BaseModel):
    location: str | None = None
    min_price: int | None = None
    max_price: int | None = None
    bedrooms_min: int | None = None
    bedrooms_max: int | None = None
    bathrooms_min: int | None = None
    bathrooms_max: int | None = None
    status: PropertyStatus | None = None
```

## Eval set format

```json
[
  {"query": "2个卧室以上 预算2000万", "expected": {"bedrooms_min": 2, "max_price": 20000000}},
  {"query": "more than 2 bedrooms under 8000000 hkd", "expected": {"bedrooms_min": 3, "max_price": 8000000}}
]
```

Pass threshold: >= 80% of queries; all non-null expected fields must match exactly.
