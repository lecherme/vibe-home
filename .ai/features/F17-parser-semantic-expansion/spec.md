# F17 — Parser Semantic Expansion: Subjective Comparisons

## Background

F16 shipped `_normalize_query` for explicit comparators (以上/以下/at least/more than). A documented limitation: subjective comparisons where the user gives a reference count N and a judgment word are not extracted.

Examples not handled by F16:
- `两个浴室太少` → no filter produced
- `三个卧室不够用 预算2000万` → no bedrooms filter, only max_price
- `浴室感觉不够用` → subjective part ignored

Regex alone cannot reliably cover the variety of natural language expression here. The correct split: LLM identifies the semantic label and reference value; deterministic code maps them to filter bounds.

## Goal

Extend `_parse_filters` to recognize subjective room-count comparisons via a controlled LLM output schema. LLM identifies `subjective_label` + `reference_value`; deterministic rules convert those to `bedrooms_min/max` or `bathrooms_min/max`. LLM never directly writes filter bounds.

## Controlled Semantic Enum

| Label | Chinese examples | English examples | Filter rule |
|-------|-----------------|-----------------|-------------|
| `insufficient` | 太少、不够、不够用、不足、偏少 | too few, not enough, insufficient | `_min = N + 1` |
| `excessive` | 太多、过多、偏多 | too many, too much, excessive | `_max = N - 1` |
| `adequate` | 够用、刚好、正好、合适 | enough, just right, sufficient | no filter (preference signal only) |
| `unknown` | unclear or no count N stated | — | no filter |

## Architecture

`_parse_filters` already makes one LLM call for `location`, `status`, `remainder`. F17 extends that same call to also return subjective room-count fields. No second LLM call is added.

```
_parse_filters(query):
  1. _normalize_query(query)                [F16]
       → deterministic fields: min_price, max_price, bedrooms_min/max, bathrooms_min/max
       → remaining_query

  2. If remaining_query: LLM call           [extended in F17]
       existing fields: location, status, remainder
       new fields:      bedrooms_subjective_label, bedrooms_ref
                        bathrooms_subjective_label, bathrooms_ref

  3. Deterministic label → bound mapping    [F17 — new step]
       insufficient + N, bedrooms_min not already set → bedrooms_min = N + 1
       excessive    + N, bedrooms_max not already set → bedrooms_max = N - 1
       adequate, unknown, or ref is null              → no filter
       Same logic for bathrooms

  4. Merge → SearchFilters
       F16 deterministic values always take priority over F17 LLM-derived values
```

**Key invariant**: LLM output schema does not include `bedrooms_min`, `bedrooms_max`, `bathrooms_min`, `bathrooms_max`. LLM cannot set filter bounds directly.

## LLM Prompt Extension

Extend the existing prompt to request four additional fields:

```
bedrooms_subjective_label : "insufficient" | "excessive" | "adequate" | "unknown" | null
bedrooms_ref              : integer | null
bathrooms_subjective_label: "insufficient" | "excessive" | "adequate" | "unknown" | null
bathrooms_ref             : integer | null
```

## Scope

- Supported: subjective comparisons for bedrooms and bathrooms in Chinese and English, with or without accompanying F16 deterministic filters.
- Not supported: no-reference expressions (no N stated), context-aware semantics, price/area subjectivity, LLM Layer 2 for fully unstructured expressions (→ F18).

## Test Strategy

### Deterministic eval — unchanged

`test_eval.py` + `eval_set.json` test `_normalize_query` in isolation. No changes; subjective cases cannot be added here (no LLM).

### Subjective integration eval — advisory

New file `backend/tests/test_subjective_eval.py`. Calls `_parse_filters` with subjective queries, asserts resulting `SearchFilters` fields. Requires live LLM API key; marked `@pytest.mark.integration`.

This eval is **informative and non-blocking**. Acceptance is not gated on its pass rate. Acceptance is determined by manual verification in T03 (see `acceptance.md`).

Minimum 8 cases covering: Chinese/English, bedrooms/bathrooms, combined with F16 filters.
