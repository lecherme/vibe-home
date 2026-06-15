# F23 — LLM Middle Layer

## Goal

Extend the existing LLM call in `_parse_filters` to recognize two fixed vocabulary categories and map them to concrete filter values. This handles vague expressions that deterministic regex cannot cover but whose thresholds are predefined — the LLM's role is term recognition, not threshold invention.

## Background

`_parse_filters` has a two-stage pipeline:

1. **Deterministic stage** — regex patterns handle explicit numeric expressions (e.g. "地铁500米内" → `subway_distance_max=500`)
2. **LLM stage** — remaining text is sent to the LLM; currently outputs `location`, `status`, subjective room labels

F23 extends the LLM stage to also output `subway_distance_max` and `built_year_min` for vague expressions.

## Fixed vocabulary

The LLM must recognize only the expressions below and return the corresponding predefined values. It must NOT invent thresholds for unlisted expressions.

### `subway_distance_max`

| Recognized expressions | Output value |
|-----------------------|--------------|
| 近地铁、靠近地铁、地铁口、步行到地铁、near MTR、close to MTR、walking distance to MTR | `subway_distance_max = 500` |

### `built_year_min`

| Recognized expressions | Output value |
|-----------------------|--------------|
| 新楼、次新楼、次新房、较新、新建、new building、newer building | `built_year_min = <current_utc_year> - 10` |

`current_utc_year` is computed by the backend and injected into the LLM prompt as a concrete 4-digit year. The LLM receives the already-computed value (e.g. `2016`) — it must not perform relative year arithmetic itself.

## Scope

### Files modified by Codex (T01 build task)

- `backend/app/services/ai_search/service.py`

### Allowed functions within the file

May modify:
- `_parse_filters` — update system prompt and merge logic for the two new output fields

Must NOT modify:
- `_relax_filters`
- `_apply_relaxation`
- `_is_property_search`
- `_resolve_result_ids`
- `_generate_summary`
- `_apply_subjective_room_filters` (unless only extending, no behaviour change to existing logic)

### Files that MUST NOT be modified

- `backend/app/schemas/search.py`
- `backend/app/schemas/ai_search.py`
- `backend/app/services/search/service.py`
- `frontend/types/search.ts`
- `backend/tests/eval_set.json`
- `backend/tests/test_eval.py`
- `.ai/features/F23-llm-middle-layer/status.json`

## Merge priority

Deterministic values always take priority over LLM values:

```
final_value = deterministic_value if deterministic_value is not None else llm_value
```

Example: "地铁500米内近地铁" — deterministic sets `subway_distance_max=500`, LLM also outputs 500; deterministic wins and the values happen to match. If deterministic had set 300, it stays 300.

## Validation of LLM outputs

Before merging:
- `subway_distance_max`: must be a positive integer in range 50–5000; drop otherwise
- `built_year_min`: must be a 4-digit integer in range 1900–`current_utc_year + 1`; drop otherwise

Invalid values are silently dropped.

## Non-goals

- No family-size / occupant-count → bedrooms_min mapping (deferred)
- No `area_min`/`area_max` LLM inference (no anchor → not safe)
- No new schema or API fields
- No frontend changes
- No eval set changes
