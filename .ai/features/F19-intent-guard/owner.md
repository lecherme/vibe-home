# F19 Intent Guard — Ownership Boundaries

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
- `.ai/features/F19-intent-guard/status.json`

**强制约束：**
- `_is_property_search` 只做二分类（`True` / `False`），不返回 intent 枚举或额外字段
- LLM fallback 只在关键词启发式无法判断时调用，不作为默认路径
- Non-search early return 使用现有 `AiSearchResult` 结构，`items=[]`、`total=0`、`query_parsed=False`
- `import app.main` exit 0
- F16 eval 30/30 不受影响

---

## T02 (Codex) — Review

只读审查，不得修改任何源文件。

---

## T03 (Claude) — Acceptance

**允许修改的文件：**
- `.ai/features/F19-intent-guard/status.json`
- `.ai/features/F19-intent-guard/final-report.md`

---

## Boundary Rules

1. Workers 不得修改 `status.json`
2. 不新增任何 schema 字段，不改 frontend，不改 LLM service
3. `eval_set.json` 和 `test_eval.py` 在 F19 中不得修改
4. Intent guard 是纯后端 service 层改动，不触碰 API 层、schema 层、embedding 层
