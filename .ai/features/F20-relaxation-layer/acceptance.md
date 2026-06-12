# F20 Acceptance Criteria

## Structural (A1–A4) — code inspection

| ID | Criterion |
|----|-----------|
| A1 | `_relax_filters(filters) -> tuple[SearchFilters, str] \| None` exists; applies exactly one step per call; returns `None` when no soft constraint remains |
| A2 | `_apply_relaxation(query, filters, query_parsed)` exists; loops `_relax_filters` (max 3 steps); calls `_resolve_result_ids` after each step; stops when `len(result_ids) >= _RELAX_SUPPLEMENT_THRESHOLD` or steps exhausted; returns `(result_ids, final_filters, relaxed_conditions)` |
| A3 | `_generate_summary` signature includes `relaxed_conditions: list[str]` parameter (default `[]`); includes it in LLM prompt when non-empty |
| A4 | Hard constraints (`max_price`, `min_price`, `status`) are never modified by `_relax_filters`; verified by `_relax_filters(SearchFilters(max_price=5000000))` → `None` |

## `_relax_filters` unit tests (A5) — deterministic, no dataset dependency

| Input | Expected output |
|-------|----------------|
| `SearchFilters(bedrooms_min=3)` | `SearchFilters(bedrooms_min=2)` + non-empty description |
| `SearchFilters(bedrooms_min=1)` | `SearchFilters(bedrooms_min=None)` + non-empty description |
| `SearchFilters(bathrooms_min=2)` | `SearchFilters(bathrooms_min=1)` + non-empty description |
| `SearchFilters(location="嘉定")` | `SearchFilters(location=None)` + non-empty description |
| `SearchFilters()` | `None` |
| `SearchFilters(max_price=5000000)` | `None` |

**A5:** All rows above pass.

## Rescue path — helper-level (A6)

Reviewer identifies `F_zero`: a `SearchFilters` where `len(_resolve_result_ids("test", F_zero, True)) == 0`.

| ID | Check |
|----|-------|
| A6 | `result_ids, _, relaxed_conditions = _apply_relaxation("test", F_zero, True)` → `relaxed_conditions` non-empty; `len(result_ids) >= 0` (may still be 0 if no soft constraint helps, but relaxation was attempted) |

## Rescue path — ai_search-level (A7)

| ID | Check |
|----|-------|
| A7 | `ai_search` called with a query that deterministically parses to `F_zero` in the current dataset returns `ai_summary` that is non-empty and not equal to `_NON_SEARCH_REDIRECT_MESSAGE` |

## Supplement path — helper-level (A8)

Reviewer identifies `F_few`: a `SearchFilters` where `0 < len(_resolve_result_ids("test", F_few, True)) < _RELAX_SUPPLEMENT_THRESHOLD`.

| ID | Check |
|----|-------|
| A8 | `strict_ids = _resolve_result_ids("test", F_few, True)`; `relaxed_ids, _, relaxed_conditions = _apply_relaxation("test", F_few, True)`; verify `len(relaxed_ids) >= len(strict_ids)` and `relaxed_conditions` non-empty |

## Supplement path — ai_search-level (A9)

| ID | Check |
|----|-------|
| A9 | `ai_search` called with a query that parses to `F_few` returns `total > 0` and `ai_summary` non-empty |

## No-relaxation guard (A10)

| ID | Check |
|----|-------|
| A10 | `_apply_relaxation("test", F_any, False)` (with `query_parsed=False`) returns `([], F_any, [])` — relaxation skipped entirely when query was not parsed |

## Regression (A11–A12)

| ID | Criterion |
|----|-----------|
| A11 | `ai_search("2 bedrooms", 1, 10)` returns `total >= _RELAX_SUPPLEMENT_THRESHOLD`; no relaxation is triggered (code path verified by inspection: relaxation branch gated by `strict_count < _RELAX_SUPPLEMENT_THRESHOLD`) |
| A12 | `test_eval.py` and `eval_set.json` unchanged; F16 eval 30/30 unaffected |
