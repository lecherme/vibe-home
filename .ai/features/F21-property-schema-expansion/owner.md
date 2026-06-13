# F21 Property Schema Expansion — Ownership Boundaries

---

## T01 (Codex) — Implementation

**允许修改的文件：**
- `backend/migrations/004_add_property_fields.sql`（新建）
- `backend/seeds/002_seed_property_fields.sql`（新建）
- `backend/app/schemas/property.py`
- `backend/app/schemas/admin.py`
- `backend/app/services/embeddings/service.py`
- `backend/app/services/admin/service.py`
- `backend/app/api/v1/admin/router.py`
- `frontend/types/property.ts`

**不得修改：**
- `backend/app/schemas/search.py`（`SearchFilters` 不新增字段）
- `frontend/types/search.ts`
- `backend/tests/eval_set.json`
- `backend/tests/test_eval.py`
- `backend/migrations/001_create_properties.sql`（只能新建迁移，不能改已有迁移）
- `backend/seeds/001_seed_properties.sql`（只能新建 seed 文件，不能改已有 seed）
- `.ai/features/F21-property-schema-expansion/status.json`

**强制约束：**
- 新字段在 DB 层可空（`built_year`、`subway_distance_m`），`tags` 不可空且默认 `'{}'`
- Seed backfill 必须覆盖 seed 数据集中所有现有 mock 房源，每条均提供非 null 值
- `import app.main` exit 0（python 导入不报错）
- F16 eval 30/30 不受影响（eval 文件不修改）

---

## T02 (Codex) — Review

只读审查，不得修改任何源文件。

---

## T03 (Claude) — Acceptance

**允许修改的文件：**
- `.ai/features/F21-property-schema-expansion/status.json`
- `.ai/features/F21-property-schema-expansion/final-report.md`

---

## Boundary Rules

1. Workers 不得修改 `status.json`
2. `SearchFilters` 在 F21 中不变；filter 扩展是 F22（LLM 中间层）的工作
3. `eval_set.json` 和 `test_eval.py` 在 F21 中不得修改
4. 迁移和 seed 文件只能新建，不能修改已有文件
