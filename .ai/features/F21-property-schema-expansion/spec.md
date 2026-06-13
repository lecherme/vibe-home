# F21 — Property Schema Expansion

## Goal

Add three new fields to the property data model so that semantic search and downstream LLM features have richer signal to work with.

`area_sqm` already exists in the DB and schema. This feature adds the remaining three fields from the backlog.

## Fields to Add

| Field | DB type | Nullable | Default | Purpose |
|-------|---------|----------|---------|---------|
| `built_year` | `integer` | yes | `NULL` | Year property was built; used by LLM middle layer for age-based filtering |
| `subway_distance_m` | `integer` | yes | `NULL` | Distance in metres to nearest MTR station; key attribute for HK property search |
| `tags` | `text[]` | no | `'{}'` | Free-form descriptive tags (e.g. `近地铁`, `装修好`, `采光好`); included in embedding text |

## Scope

### Files modified by Codex (T01 build task)

- `backend/migrations/004_add_property_fields.sql` — ALTER TABLE to add three columns
- `backend/seeds/002_seed_property_fields.sql` — UPDATE all 20 existing properties with plausible HK values
- `backend/app/schemas/property.py` — add three fields to `Property`
- `backend/app/schemas/admin.py` — add three fields to `PropertyCreate` and `PropertyUpdate`
- `backend/app/services/embeddings/service.py` — extend `_build_embedding_text` and `try_upsert_property_embedding` to include new fields
- `backend/app/services/admin/service.py` — pass new fields when calling `try_upsert_property_embedding` in `create_property` and `update_property`
- `backend/app/api/v1/admin/router.py` — pass new fields in `sync_property_embeddings`
- `frontend/types/property.ts` — add three fields to `Property` interface

### Files that MUST NOT be modified

- `backend/app/schemas/search.py` — `SearchFilters` is unchanged; no new filter fields in F21
- `frontend/types/search.ts` — unchanged
- `backend/tests/test_eval.py` — unchanged
- `backend/tests/eval_set.json` — unchanged
- `backend/migrations/001_create_properties.sql` — ALTER TABLE goes in a new migration file, not in the original

## Embedding text contract

`_build_embedding_text` must produce richer text that includes the new fields when present:

```
{title}. {description}. Located in {location}. Area: {area_sqm}sqm. Built: {built_year}. Distance to subway: {subway_distance_m}m. Tags: {tag1}, {tag2}.
```

Fields that are `None`/empty are omitted from the text.

## Seed data requirements

`002_seed_property_fields.sql` must provide UPDATE statements for all 20 existing properties (`prop-hk-001` through `prop-hk-020`) with:
- `built_year`: integer in range [1970, 2023], realistic for HK
- `subway_distance_m`: integer in range [100, 1500], realistic walking distance to MTR
- `tags`: non-empty array, 2–5 tags per property in Chinese or English matching the property description

## Non-goals

- No changes to `SearchFilters` — filter expansion is F22 (LLM middle layer)
- No automatic re-embedding of existing properties — re-embedding is a one-time admin operation done via `POST /api/v1/admin/embeddings/sync` after migration
- No frontend display changes — new fields are in the API response; UI update is a separate ticket
