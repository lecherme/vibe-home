# F17 Parser Semantic Expansion — Ownership Boundaries

---

## T01 (Codex) — Backend

**允许修改的文件：**
- `backend/app/services/ai_search/service.py`
- `backend/tests/test_subjective_eval.py`（新建）

**不得修改：** `frontend/`、`backend/app/schemas/`、`backend/tests/eval_set.json`、`backend/tests/test_eval.py`、`status.json`

**强制约束：**
- LLM prompt 不得包含 `bedrooms_min/max`、`bathrooms_min/max` 作为输出字段
- F16 deterministic 值优先级高于 F17 LLM-derived 值
- `import app.main` exit 0
- `test_eval.py` (F16) 仍须 >= 80% pass

---

## T02 (Codex) — Review

只读审查，不得修改任何源文件。

---

## T03 (Claude) — Acceptance

**允许修改的文件：**
- `.ai/features/F17-parser-semantic-expansion/status.json`
- `.ai/features/F17-parser-semantic-expansion/final-report.md`

---

## Boundary Rules

1. Workers 不得修改 `status.json`
2. LLM 不得直接输出 filter bound 字段（`bedrooms_min/max`、`bathrooms_min/max`）
3. `eval_set.json` 和 `test_eval.py` 不得在 F17 中修改（属于 F16 deterministic eval）
4. Frontend 无需改动（filter chips 已正确显示 `>= X Beds` / `<= X Beds`）
