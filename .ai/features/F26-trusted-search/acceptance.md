# F26 Acceptance Criteria

## Constraint enforcement

| ID | Criterion |
|----|-----------|
| A1 | `_relax_filters` does not contain logic that reduces or removes `bedrooms_min` |
| A2 | `_relax_filters` does not contain logic that reduces or removes `bathrooms_min` |
| A3 | `_relax_filters` removes `subway_distance_max` when it is set (soft constraint) |
| A4 | `_relax_filters` removes `built_year_min` when it is set (soft constraint) |
| A5 | Relaxation order in `_relax_filters`: `subway_distance_max` → `built_year_min` → `location` |

## Hard-filter revalidation

| ID | Criterion |
|----|-----------|
| A6 | `_matches_hard_constraints` exists and checks: `max_price`, `min_price`, `bedrooms_min`, `bedrooms_max`, `bathrooms_min`, `bathrooms_max`, `area_min`, `area_max` |
| A7 | No property in `strict_items` violates any hard constraint; verified across all F26 eval queries |

## Hybrid scoring

| ID | Criterion |
|----|-----------|
| A8 | `_resolve_result_ids` uses score fusion: semantic ids contribute `1/(rank+1)`, filter ids contribute `+0.8`; results sorted descending by score |
| A9 | A property appearing in both semantic and filter results scores higher than one appearing in only one source |

## API contract

| ID | Criterion |
|----|-----------|
| A10 | `AiSearchResult` includes `strict_items`, `recommended_items`, `relaxations`, `parsed_constraints`, `match_reasons` |
| A11 | `items` = `strict_items + recommended_items` (strict first); `total` = combined count |
| A12 | `relaxations` is empty when no relaxation occurred; contains `{field, from_value, to_value}` records when relaxation occurred |
| A13 | `parsed_constraints` reflects the original `parsed_filters` (pre-relaxation) with `strength` and `label` for each non-None field |
| A14 | `match_reasons` is keyed by property id; each entry lists reasons with `field`, `label`, `matched`, `strength` |
| A15 | `parsed_filters` (original intent) is unchanged — BUG-025 non-regression |

## Frontend

| ID | Criterion |
|----|-----------|
| A16 | Search results page renders two zones when both `strict_items` and `recommended_items` are non-empty |
| A17 | Relaxation notice appears above recommended zone, derived from `relaxations` |
| A18 | Each card shows match reason chips; unmatched soft reasons shown with △ symbol |
| A19 | When `recommended_items` is empty, no empty recommended zone is shown |
| A20 | `npx tsc --noEmit` exits 0 |

## Evaluation

| ID | Criterion |
|----|-----------|
| A21 | `eval_set_f26.json` contains ≥10 queries covering: hard-only, soft-only, mixed, Chinese vocab, no-relaxation, zero-results, non-search |
| A22 | F26 eval passes all hard-filter precision assertions (0 violations) |
| A23 | F26 eval passes all strict/recommended split correctness assertions for queries that trigger relaxation |
| A24 | F16 eval still passes 30/30 after F26 changes (`bash tools/run_eval.sh` unchanged) |

## Non-regression

| ID | Criterion |
|----|-----------|
| A25 | `_generate_summary` source unchanged |
| A26 | `_parse_filters` source unchanged |
| A27 | `_is_property_search` source unchanged |
| A28 | `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exits 0 |
