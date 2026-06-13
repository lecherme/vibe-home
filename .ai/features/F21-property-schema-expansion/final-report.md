# F21 Final Report

## Disposition: ACCEPTED

## Criteria Results

| ID | Criterion | Result | Notes |
|----|-----------|--------|-------|
| A1 | Migration adds `built_year`, `subway_distance_m`, `tags` columns | PASS | `004_add_property_fields.sql:1` |
| A2 | `Property` schema exposes three new fields with correct nullability | PASS | `property.py:22-24` |
| A3 | `PropertyCreate` and `PropertyUpdate` accept the three new fields | PASS | `admin.py:6` |
| A4 | Frontend `Property` interface declares matching types | PASS | `property.ts:12-14` |
| A5 | `_build_embedding_text` includes new fields when present | PASS | `embeddings/service.py:31` |
| A6 | `try_upsert_property_embedding` and all call sites pass new fields | PASS | `service.py:70`, `admin/service.py:36`, `router.py:42` |
| A7 | Seed backfill covers all 20 mock properties with plausible HK values | PASS | `002_seed_property_fields.sql:11` |
| A8 | `SearchFilters` unchanged | PASS | `git diff` empty on `search.py` |
| A9 | `frontend/types/search.ts` unchanged | PASS | `git diff` empty |
| A10 | `eval_set.json` and `test_eval.py` unchanged | PASS | `git diff` empty |
| A11 | `import app.main` exits 0 | PASS | Verified in container |
| A12 | F16 eval 30/30 unaffected | PASS | `docker compose run --rm backend pytest tests/test_eval.py` — 30/30 confirmed |

## Summary

F21 is complete. Three new fields are added to the property data model:

- **`built_year`** (`integer`, nullable) — year built; plausible HK values seeded for all 20 mock properties
- **`subway_distance_m`** (`integer`, nullable) — distance to nearest MTR in metres; plausible values seeded
- **`tags`** (`text[]`, not null, default `{}`) — descriptive tags; non-empty arrays seeded for all 20 mock properties

Changes span DB migration, backend schemas, admin API schemas, embedding text generation, and frontend type declarations. `SearchFilters` is unchanged — filter expansion is deferred to F22.

One direct_fixup applied after T02 Run 1: `frontend/types/admin.ts` was missing the three new fields on `AdminPropertyCreate` / `AdminPropertyUpdate`. Scope was expanded, fix applied, and T02 rerun as review_rerun — all criteria passed.

No eval files modified. F16 eval unaffected.
