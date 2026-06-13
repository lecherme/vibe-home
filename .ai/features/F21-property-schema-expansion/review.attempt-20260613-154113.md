# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | [`backend/migrations/004_add_property_fields.sql`](/home/lecherme/workspace/vibe-home/backend/migrations/004_add_property_fields.sql:1) exists and adds `built_year`, `subway_distance_m`, and `tags text[] not null default '{}'::text[]`. |
| A2 | PASS | [`backend/app/schemas/property.py`](/home/lecherme/workspace/vibe-home/backend/app/schemas/property.py:13) exposes `built_year: int \| None`, `subway_distance_m: int \| None`, and `tags: list[str]` with `default_factory=list`. |
| A3 | PASS | [`backend/app/schemas/admin.py`](/home/lecherme/workspace/vibe-home/backend/app/schemas/admin.py:6) accepts all three fields on `PropertyCreate` and `PropertyUpdate`. |
| A4 | PASS | [`frontend/types/property.ts`](/home/lecherme/workspace/vibe-home/frontend/types/property.ts:3) declares `built_year: number \| null`, `subway_distance_m: number \| null`, and `tags: string[]`. |
| A5 | PASS | [`backend/app/services/embeddings/service.py`](/home/lecherme/workspace/vibe-home/backend/app/services/embeddings/service.py:31) includes `area_sqm`, `built_year`, `subway_distance_m`, and `tags` in `_build_embedding_text` when present. |
| A6 | PASS | [`try_upsert_property_embedding`](/home/lecherme/workspace/vibe-home/backend/app/services/embeddings/service.py:70) accepts the new fields, and all three call sites pass them in [`backend/app/services/admin/service.py`](/home/lecherme/workspace/vibe-home/backend/app/services/admin/service.py:36) and [`backend/app/api/v1/admin/router.py`](/home/lecherme/workspace/vibe-home/backend/app/api/v1/admin/router.py:42). |
| A7 | PASS | [`backend/seeds/002_seed_property_fields.sql`](/home/lecherme/workspace/vibe-home/backend/seeds/002_seed_property_fields.sql:11) updates `prop-hk-001` through `prop-hk-020`; all rows have in-range `built_year`, `subway_distance_m`, and non-empty tag arrays. |
| A8 | PASS | `git diff origin/main..HEAD -- backend/app/schemas/search.py` is empty; [`SearchFilters`](/home/lecherme/workspace/vibe-home/backend/app/schemas/search.py:6) has no new fields. |
| A9 | PASS | `git diff origin/main..HEAD -- frontend/types/search.ts` is empty. |
| A10 | PASS | `git diff origin/main..HEAD -- backend/tests/eval_set.json backend/tests/test_eval.py` is empty. |
| A11 | PASS | `docker compose exec -T backend python3 -c "import app.main; print('OK')"` returned `OK`. |
| A12 | PASS | `docker compose run --rm -v /home/lecherme/workspace/vibe-home/backend/tests:/app/tests:ro backend pytest tests/test_eval.py` passed: `2 passed`. |
| API types published to `frontend/types/` | FAIL | [`frontend/types/admin.ts`](/home/lecherme/workspace/vibe-home/frontend/types/admin.ts:1) still omits `built_year`, `subway_distance_m`, and `tags`, while the backend admin API accepts them in [`backend/app/schemas/admin.py`](/home/lecherme/workspace/vibe-home/backend/app/schemas/admin.py:6). |
| Frontend business-logic boundary | PASS | No frontend component files changed for F21; the only frontend product-code diff is [`frontend/types/property.ts`](/home/lecherme/workspace/vibe-home/frontend/types/property.ts:3). |
| `status.json` not modified by Codex/Gemini | PASS | `.ai/.../status.json` is modified in the workspace, but the activity log attributes status updates to `claude`, not Codex or Gemini. |

## Issues Found
- BLOCKER: [`frontend/types/admin.ts`](/home/lecherme/workspace/vibe-home/frontend/types/admin.ts:1) is stale. `AdminPropertyCreate` and `AdminPropertyUpdate` do not publish `built_year`, `subway_distance_m`, or `tags`, so the frontend type layer no longer matches the backend admin API contract.
- WARNING: There is no direct automated coverage for the new admin-field propagation or embedding-text expansion paths. Eval regression coverage passed, but `_build_embedding_text` and admin create/update propagation remain untested.

## Required Fixes
- Update [`frontend/types/admin.ts`](/home/lecherme/workspace/vibe-home/frontend/types/admin.ts:1) so `AdminPropertyCreate` and `AdminPropertyUpdate` include `built_year?: number | null`, `subway_distance_m?: number | null`, and `tags?: string[]` to match the backend admin schemas.

## Approved Items
- Migration and backend schemas implement the three new property fields correctly.
- Embedding generation and manual embedding sync include the new metadata.
- Seed backfill covers all 20 existing Hong Kong properties with plausible values.
- `SearchFilters`, frontend search types, and eval files remained unchanged.
- Runtime verification passed for `import app.main` and the F16 eval test.
