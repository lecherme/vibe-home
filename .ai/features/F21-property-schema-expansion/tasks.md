# F21 Tasks

## T01 — Codex: implement property schema expansion

**Owner:** codex
**Type:** build
**Depends on:** —

**Scope:**
- `backend/migrations/004_add_property_fields.sql`
- `backend/seeds/002_seed_property_fields.sql`
- `backend/app/schemas/property.py`
- `backend/app/schemas/admin.py`
- `backend/app/services/embeddings/service.py`
- `backend/app/services/admin/service.py`
- `backend/app/api/v1/admin/router.py`
- `frontend/types/property.ts`
- `frontend/types/admin.ts`

**Done condition:**
- Migration file adds `built_year`, `subway_distance_m`, `tags` columns to the properties table with correct nullability
- Backend `Property` schema exposes the three new fields with appropriate nullability/default semantics
- Admin create/update schemas accept the three new fields
- `_build_embedding_text` includes the new fields in the output text when present
- `try_upsert_property_embedding` and all its call sites pass the new fields
- Frontend `Property` type exposes the three new fields matching backend nullability
- Seed backfill file provides plausible HK values for all 20 existing mock properties (`prop-hk-001` through `prop-hk-020`)
- `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exits 0

---

## T02 — Codex: review

**Owner:** codex
**Type:** review
**Depends on:** T01

---

## T03 — Claude: acceptance

**Owner:** claude
**Type:** acceptance
**Depends on:** T02
