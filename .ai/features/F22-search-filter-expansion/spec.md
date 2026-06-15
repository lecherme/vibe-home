# F22 — Search Filter Expansion

## Goal

Extend `SearchFilters` with four new fields backed by the F21 property schema columns, and wire them through the search pipeline so deterministic parsing and filter-based search actually use them.

This is purely a capability layer — no LLM involvement. F23 will add LLM interpretation of ambiguous expressions on top of this.

## New Fields

| Field | Type | Semantics |
|-------|------|-----------|
| `area_min` | `int \| None` | Minimum `area_sqm` in sqm (inclusive) |
| `area_max` | `int \| None` | Maximum `area_sqm` in sqm (inclusive) |
| `built_year_min` | `int \| None` | Earliest acceptable build year (inclusive) |
| `subway_distance_max` | `int \| None` | Maximum distance to nearest MTR in metres (inclusive) |

## Scope

### Files modified by Codex (T01 build task)

- `backend/app/schemas/search.py` — add four fields to `SearchFilters`
- `backend/app/services/search/service.py` — apply four new filters in `search()`
- `backend/app/services/ai_search/service.py` — add deterministic regex patterns; update `_normalize_filters` and `_has_filters`
- `frontend/types/search.ts` — add four fields to `SearchFilters` interface

### Allowed functions within `backend/app/services/ai_search/service.py`

May modify: `_parse_filters`, `_normalize_filters`, `_has_filters`

Must NOT modify: `_relax_filters`, `_apply_relaxation` — relaxation of new fields is deferred

### Files that MUST NOT be modified

- `backend/app/schemas/property.py`
- `backend/tests/eval_set.json`
- `backend/tests/test_eval.py`
- `.ai/features/F22-search-filter-expansion/status.json`

## Deterministic parsing patterns

`_parse_filters` must extract new fields only from expressions with explicit numbers or fixed known mappings. Vague expressions ("新楼", "近地铁" without a distance number) are F23 territory — do not handle them here.

### `area_min` / `area_max`

| Expression | Result |
|-----------|--------|
| `100平以上` / `100㎡以上` / `100平米以上` | `area_min=100` |
| `100平以下` / `100㎡以下` | `area_max=100` |
| `80到120平` / `80-120平` / `80至120平` | `area_min=80, area_max=120` |
| `at least 80 sqm` / `over 100 sqm` | `area_min=80` / `area_min=100` |
| `under 60 sqm` / `below 60 sqm` | `area_max=60` |

### `built_year_min`

"Current year" means the server's UTC year at parse time.

| Expression | Result |
|-----------|--------|
| `2010年后` / `2010年以后` | `built_year_min=2010` |
| `房龄10年内` / `楼龄10年内` / `10年楼龄以内` | `built_year_min=current_year - 10` |
| `built after 2015` / `newer than 2015` | `built_year_min=2015` |
| `within 5 years` / `less than 5 years old` | `built_year_min=current_year - 5` |

### `subway_distance_max`

| Expression | Result |
|-----------|--------|
| `地铁500米内` / `距地铁500米以内` | `subway_distance_max=500` |
| `MTR within 500m` / `500m from MTR` | `subway_distance_max=500` |
| `within 300 metres of MTR` | `subway_distance_max=300` |

## Non-goals

- No LLM calls for new fields (F23)
- No relaxation of new fields (deferred)
- No frontend UI changes — new fields are in the type layer only
- `tags` is not a filter target in F22 — requires a controlled vocabulary first
- No changes to `AiSearchResult` schema
