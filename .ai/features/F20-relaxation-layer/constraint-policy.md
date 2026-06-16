# Search Constraint Policy

Defines which search filters are **hard constraints** (never auto-relaxed) and which are **soft constraints** (eligible for automatic relaxation when strict results are insufficient). All downstream work — BUG-022, relaxation改造, hybrid ranking, strict/broadened split — should reference this document.

---

## Hard Constraints

Never touched by `_relax_filters` or `_apply_relaxation`. If strict results are 0 and only hard constraints remain, the system returns 0 results and discloses that — it does not silently widen.

| Field | Rationale |
|---|---|
| `price_max` | Budget ceiling is a non-negotiable user limit |
| `price_min` | Budget floor (when present) same as above |
| `bedrooms_min` | Room count is a concrete household need; silently reducing it misleads the user |
| `bedrooms_max` | Upper bound is equally concrete |
| `bathrooms_min` | Same as bedrooms |
| `bathrooms_max` | Same as bedrooms |
| `area_min` | Explicit size floor |
| `area_max` | Explicit size ceiling |

### Delta from current code

`_relax_filters()` currently relaxes `bedrooms_min` and `bathrooms_min` (reduces by 1, then removes). **This contradicts the policy above.** When relaxation改造 lands, these fields must be removed from the relaxation sequence.

---

## Soft Constraints

May be auto-relaxed when strict results are 0 or below `_RELAX_SUPPLEMENT_THRESHOLD`. Relaxation must always be disclosed explicitly to the user (field name, original value → relaxed value).

| Field | Default relaxation |
|---|---|
| `subway_distance_max` | Remove (distance preference, not a hard requirement) |
| `built_year_min` | Remove (recency preference) |

---

## Conditional Constraints

Classification depends on how the field was populated.

| Field | Hard when | Soft when |
|---|---|---|
| `location` | Parser matched a specific named district or area (e.g. "西贡", "港岛") | Populated from vague semantic preference (e.g. "安静的地方") |

**Implementation note:** the parser does not currently distinguish these two cases. Until it does, `location` should be treated as **soft** (current behavior) to avoid over-blocking.

---

## Strict vs. Broadened Result Contract

**Strict result:** a property that satisfies all hard constraints AND all soft constraints as originally parsed.

**Broadened result:** a property that satisfies all hard constraints, but one or more soft constraints have been relaxed. Hard constraints are never relaxed even in the broadened set.

When both strict and broadened results are returned together, the API response must indicate which items are which (future `match_type` field) and disclose exactly which soft constraints were relaxed and to what value.

---

## Relaxation Disclosure Contract

Every auto-relaxation must be surfaced to the user as a structured record:

```json
{ "field": "subway_distance_max", "from": 500, "to": null }
{ "field": "built_year_min", "from": 2014, "to": null }
```

Free-text descriptions (`relaxed_conditions` string list) are acceptable as an interim format but should be migrated to structured objects when the frontend is ready to consume them.
