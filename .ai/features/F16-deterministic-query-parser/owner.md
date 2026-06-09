# F16 Deterministic Query Parser — Ownership Boundaries

---

## T01 (Codex) — Backend

**允许修改的文件：**
- `backend/app/schemas/search.py`
- `backend/app/services/search/service.py`
- `backend/app/services/ai_search/service.py`
- `backend/app/api/v1/search/router.py`（query params 更名）
- `backend/tests/eval_set.json`（新建）
- `backend/tests/test_eval.py`（新建）
- `backend/tests/test_search.py`（更新旧字段引用）

**不得修改：** `frontend/`、`backend/app/schemas/ai_search.py`（除非 SearchFilters 引用需要同步）、`status.json`

**强制约束：**
- `_normalize_query` 必须纯 deterministic，不得调用 LLM
- 所有测试通过：`import app.main` exit 0，eval set >= 80% pass

---

## T02 (Gemini) — Frontend

**允许修改的文件：**
- `frontend/types/search.ts`
- `frontend/components/features/search/ai-parsed-filters-card.tsx`
- `frontend/lib/api/search.ts`（如有 bedrooms/bathrooms query param 构造）
- `frontend/app/(dashboard)/search/page.tsx`（如有 filter form 字段）

**不得修改：** `backend/`、`status.json`

**强制约束：**
- Filter Search 现有功能不得退化
- `tsc --noEmit` exit 0

---

## T03 (Codex) — Review

只读审查，不得修改任何源文件。

---

## T04 (Claude) — Acceptance

**允许修改的文件：**
- `.ai/features/F16-deterministic-query-parser/status.json`
- `.ai/features/F16-deterministic-query-parser/final-report.md`

---

## Boundary Rules

1. Workers 不得修改 `status.json`
2. `_normalize_query` 不得依赖 LLM
3. `SearchFilters` 改动必须同时在 backend schema 和 frontend types 中体现，两边必须一致
4. Regular search endpoint query params 必须向后兼容或同步更新前端调用方
