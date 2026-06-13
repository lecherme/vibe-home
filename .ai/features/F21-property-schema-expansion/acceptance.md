# F21 Acceptance Criteria

## Schema & Migration

| ID | Criterion |
|----|-----------|
| A1 | `backend/migrations/004_add_property_fields.sql` exists and contains `ALTER TABLE` statements adding `built_year` (integer, nullable), `subway_distance_m` (integer, nullable), and `tags` (text array, not null, default empty) |
| A2 | `backend/app/schemas/property.py` `Property` model exposes `built_year` (nullable integer), `subway_distance_m` (nullable integer), and `tags` (list of strings, default empty) |
| A3 | `backend/app/schemas/admin.py` `PropertyCreate` accepts all three new fields as optional inputs; `PropertyUpdate` accepts them as optional patch fields |
| A4 | `frontend/types/property.ts` `Property` interface declares `built_year: number | null`, `subway_distance_m: number | null`, `tags: string[]` |

## Embedding

| ID | Criterion |
|----|-----------|
| A5 | `_build_embedding_text` in `embeddings/service.py` produces output that includes `area_sqm`, `built_year`, `subway_distance_m`, and `tags` content when those values are present/non-empty |
| A6 | `try_upsert_property_embedding` signature accepts the new fields; all three call sites (`create_property`, `update_property`, `sync_property_embeddings`) pass them |

## Seed Data

| ID | Criterion |
|----|-----------|
| A7 | `backend/seeds/002_seed_property_fields.sql` exists with UPDATE statements covering all existing mock properties in `001_seed_properties.sql`; each row gets a non-null `built_year` in a plausible HK range, a non-null `subway_distance_m` in a plausible walking-distance range, and a non-empty `tags` array |

## Non-regression

| ID | Criterion |
|----|-----------|
| A8 | `backend/app/schemas/search.py` `SearchFilters` is unchanged — no new filter fields added |
| A9 | `frontend/types/search.ts` is unchanged |
| A10 | `backend/tests/eval_set.json` and `backend/tests/test_eval.py` are unchanged |
| A11 | `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exits 0 |
| A12 | F16 eval passes 30/30 after F21 changes — run `backend/tests/test_eval.py` and confirm no regressions |
