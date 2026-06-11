# F18 Parser Room Vocabulary — Ownership Boundaries

---

## T01 (Codex) — Implementation

**允许修改的文件：**
- `backend/app/services/ai_search/service.py`

**不得修改：** `frontend/`、`backend/app/schemas/`、`backend/tests/eval_set.json`、`backend/tests/test_eval.py`、`status.json`、`backend/app/services/llm/`

**强制约束：**
- `室`/`卧`/`卫` 只能在数字绑定的提取 pattern 内匹配，不得加为全局 alternation
- bare count 提取必须在 comparator 提取之后运行，避免 double-match
- `import app.main` exit 0
- F16 eval 30/30

---

## T02 (Codex) — Review

只读审查，不得修改任何源文件。

---

## T03 (Claude) — Acceptance

**允许修改的文件：**
- `.ai/features/F18-parser-room-vocab/status.json`
- `.ai/features/F18-parser-room-vocab/final-report.md`

---

## Boundary Rules

1. Workers 不得修改 `status.json`
2. 只改 `service.py`，不改 LLM prompt、schema、frontend
3. `eval_set.json` 和 `test_eval.py` 不得在 F18 中修改
