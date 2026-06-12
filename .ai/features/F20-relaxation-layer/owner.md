# F20 Relaxation Layer — Ownership Boundaries

---

## T01 (Codex) — Implementation

**允许修改的文件：**
- `backend/app/services/ai_search/service.py`

**不得修改：**
- `frontend/`
- `backend/app/schemas/`（不新增字段，不改 `AiSearchResult` / `SearchFilters`）
- `backend/tests/eval_set.json`
- `backend/tests/test_eval.py`
- `backend/app/services/llm/service.py`
- `.ai/features/F20-relaxation-layer/status.json`

**强制约束：**
- `max_price`、`min_price`、`status` 不得在 `_relax_filters` 中被修改
- 放宽顺序固定：`bedrooms_min` → `bathrooms_min` → `location`，不得重排
- relaxation 只在 `query_parsed=True` 时触发，`query_parsed=False` 时跳过
- 最多 3 步放宽，不得无限循环
- `import app.main` exit 0
- F16 eval 30/30 不受影响

---

## T02 (Codex) — Review

只读审查，不得修改任何源文件。

---

## T03 (Claude) — Acceptance

**允许修改的文件：**
- `.ai/features/F20-relaxation-layer/status.json`
- `.ai/features/F20-relaxation-layer/final-report.md`

---

## Boundary Rules

1. Workers 不得修改 `status.json`
2. 不新增任何 schema 字段，不改 frontend，不改 LLM service
3. `eval_set.json` 和 `test_eval.py` 在 F20 中不得修改
4. Relaxation 是纯 service 层改动，不触碰 API 层、schema 层、embedding 实现
