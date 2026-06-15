# F23 LLM Middle Layer — Ownership Boundaries

---

## T01 (Codex) — Implementation

**允许修改的文件：**
- `backend/app/services/ai_search/service.py`

**在文件内，允许修改的函数：**
- `_parse_filters`
- `_apply_subjective_room_filters`（只允许扩展，不得改变现有逻辑行为）

**在文件内，不得修改的函数：**
- `_relax_filters`
- `_apply_relaxation`
- `_is_property_search`
- `_resolve_result_ids`
- `_generate_summary`

**不得修改：**
- `backend/app/schemas/search.py`
- `backend/app/schemas/ai_search.py`
- `backend/app/services/search/service.py`
- `frontend/types/search.ts`
- `backend/tests/eval_set.json`
- `backend/tests/test_eval.py`
- `.ai/features/F23-llm-middle-layer/status.json`

**强制约束：**
- `current_utc_year - 10` 由 Python 计算后注入 prompt，不得由 LLM 自行推算
- LLM 输出只允许 vocabulary 表内定义的映射，不得扩展到其他字段
- 确定性解析值优先于 LLM 值
- F16 eval 30/30 不受影响
- `import app.main` exit 0

---

## T02 (Codex) — Review

只读审查，不得修改任何源文件。

---

## T03 (Claude) — Acceptance

**允许修改的文件：**
- `.ai/features/F23-llm-middle-layer/status.json`
- `.ai/features/F23-llm-middle-layer/final-report.md`
