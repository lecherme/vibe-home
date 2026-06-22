# F26 Trusted Search — Acceptance Report

**Result: PASS**
**Disposition: accepted**
**Date: 2026-06-22**

All 28 acceptance criteria passed. See verdicts below.

---

## Criteria Verdicts

| ID | Criterion | Verdict |
|----|-----------|---------|
| A1 | `_relax_filters` does not reduce/remove `bedrooms_min` | PASS |
| A2 | `_relax_filters` does not reduce/remove `bathrooms_min` | PASS |
| A3 | `_relax_filters` removes `subway_distance_max` when set | PASS |
| A4 | `_relax_filters` removes `built_year_min` when set | PASS |
| A5 | Relaxation order: `subway_distance_max` → `built_year_min` → `location` | PASS |
| A6 | `_matches_hard_constraints` checks all 8 hard fields | PASS |
| A7 | No strict_item violates hard constraints across all F26 eval queries | PASS |
| A8 | Hybrid scoring: semantic `1/(rank+1)`, filter `+0.8` | PASS |
| A9 | Property in both sources scores higher than in either alone | PASS |
| A10 | `AiSearchResult` includes all 5 new fields | PASS |
| A11 | `items = strict_items + recommended_items`; `total = combined count` | PASS |
| A12 | `relaxations` empty when no relaxation; structured when relaxed | PASS |
| A13 | `parsed_constraints` reflects pre-relaxation original filters | PASS |
| A14 | `match_reasons` keyed by property id; each entry has field/label/matched/strength | PASS |
| A15 | `parsed_filters` preserves original intent (BUG-025 non-regression) | PASS |
| A16 | Two-zone render when both strict and recommended are non-empty | PASS |
| A17 | RelaxationNotice above recommended zone, derived from `relaxations` | PASS |
| A18 | Match reason chips per card; unmatched soft reason shown with △ | PASS |
| A19 | No empty recommended zone when `recommended_items` is empty | PASS |
| A20 | `npx tsc --noEmit` exits 0 | PASS |
| A21 | ≥10 queries covering all required case types | PASS (10 queries) |
| A22 | Hard-filter precision: 0 violations across F26 eval set | PASS |
| A23 | Strict/recommended split assertions pass for all relaxation cases | PASS |
| A24 | F16 eval unchanged (`bash tools/run_eval.sh`) | PASS |
| A25 | `_generate_summary` source unchanged | PASS |
| A26 | `_parse_filters` source unchanged | PASS |
| A27 | `_is_property_search` source unchanged | PASS |
| A28 | `docker compose exec -T backend python3 -c "import app.main"` exits 0 | PASS |

---

## Open Issues (non-blocking)

1. **Stale API client type** — `frontend/lib/api/ai-search.ts` imports `AiSearchResult` from `@/types/search` instead of `@/types/ai-search`; page.tsx compensates with a cast. Fix in follow-up.

2. **run_eval.sh excludes F26 suite** — `tools/run_eval.sh` runs only F16. F26 suite must be invoked separately. Recommend extending the script.

3. **Self-referential test helpers** — `test_eval_f26.py` derives expected splits via the same service helpers under test, weakening regression detection for those helpers.
