# Review

## Verdict
PASS

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | [backend/migrations/004_add_property_fields.sql](/home/lecherme/workspace/vibe-home/backend/migrations/004_add_property_fields.sql:1) adds `built_year`, `subway_distance_m`, and `tags text[] not null default '{}'::text[]`. |
| A2 | PASS | [backend/app/schemas/property.py](/home/lecherme/workspace/vibe-home/backend/app/schemas/property.py:13) exposes `built_year: int \| None`, `subway_distance_m: int \| None`, and `tags: list[str] = Field(default_factory=list)`. |
| A3 | PASS | [backend/app/schemas/admin.py](/home/lecherme/workspace/vibe-home/backend/app/schemas/admin.py:6) accepts the three fields on both `PropertyCreate` and `PropertyUpdate`. |
| A4 | PASS | [frontend/types/property.ts](/home/lecherme/workspace/vibe-home/frontend/types/property.ts:3) declares `built_year: number \| null`, `subway_distance_m: number \| null`, and `tags: string[]`. |
| A5 | PASS | [backend/app/services/embeddings/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/embeddings/service.py:31) includes `area_sqm`, `built_year`, `subway_distance_m`, and `tags` when present, omitting nullable/empty fields. |
| A6 | PASS | [try_upsert_property_embedding](/home/lecherme/workspace/vibe-home/backend/app/services/embeddings/service.py:70) accepts the new fields, and all three call sites pass them in [backend/app/services/admin/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/admin/service.py:36) and [backend/app/api/v1/admin/router.py](/home/lecherme/workspace/vibe-home/backend/app/api/v1/admin/router.py:42). |
| A7 | PASS | [backend/seeds/002_seed_property_fields.sql](/home/lecherme/workspace/vibe-home/backend/seeds/002_seed_property_fields.sql:11) updates `prop-hk-001` through `prop-hk-020`; all 20 rows have non-null in-range `built_year`, in-range `subway_distance_m`, and non-empty tag arrays. |
| A8 | PASS | [backend/app/schemas/search.py](/home/lecherme/workspace/vibe-home/backend/app/schemas/search.py:7) remains unchanged; no new `SearchFilters` fields were added. |
| A9 | PASS | [frontend/types/search.ts](/home/lecherme/workspace/vibe-home/frontend/types/search.ts:3) remains unchanged. |
| A10 | PASS | `git diff -- backend/tests/eval_set.json backend/tests/test_eval.py` is empty; both protected eval files are unchanged. |
| A11 | PASS | `docker compose exec -T backend python3 -c "import app.main; print('OK')"` returned `OK`. |
| A12 | PASS | `docker compose run --rm -v /home/lecherme/workspace/vibe-home/backend/tests:/app/tests:ro backend pytest /app/tests/test_eval.py` passed, and a direct check over [backend/tests/test_eval.py](/home/lecherme/workspace/vibe-home/backend/tests/test_eval.py:18) reported `passing=30 total=30`. |
| API types published to `frontend/types/` | PASS | [frontend/types/admin.ts](/home/lecherme/workspace/vibe-home/frontend/types/admin.ts:1) now publishes `built_year`, `subway_distance_m`, and `tags` for the admin API alongside [frontend/types/property.ts](/home/lecherme/workspace/vibe-home/frontend/types/property.ts:3). |
| Frontend business-logic boundary | PASS | No frontend component/business-logic files were changed for F21; the frontend implementation surface is limited to type declarations. |
| `status.json` not modified by Codex or Gemini | PASS | [.ai/features/F21-property-schema-expansion/status.json](/home/lecherme/workspace/vibe-home/.ai/features/F21-property-schema-expansion/status.json:48) is currently modified, but the activity log attributes the relevant status transitions to `claude`, not Codex or Gemini. |

## Issues Found
- WARNING: No targeted automated tests were added for admin create/update propagation of the new fields or for `_build_embedding_text`; current confidence for those paths comes from code inspection plus non-regression/import checks.

## Required Fixes
- None.

## Approved Items
- Migration, backend schemas, and frontend property/admin types are aligned on the three new fields.
- Embedding text generation and all embedding upsert call sites include the new metadata.
- Seed backfill covers all 20 existing Hong Kong properties with plausible values.
- Protected search and eval files remained unchanged.
- Runtime verification passed for backend import and the full 30/30 eval set.
