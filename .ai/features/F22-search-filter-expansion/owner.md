# F22 Search Filter Expansion — Ownership Boundaries

---

## T01 (Codex) — Implementation

**允许修改的文件：**
- `backend/app/schemas/search.py`
- `backend/app/services/search/service.py`
- `backend/app/services/ai_search/service.py`
- `frontend/types/search.ts`

**在 `backend/app/services/ai_search/service.py` 内，允许修改的函数：**
- `_parse_filters`
- `_normalize_filters`
- `_has_filters`

**在 `backend/app/services/ai_search/service.py` 内，不得修改的函数：**
- `_relax_filters`
- `_apply_relaxation`

**不得修改：**
- `backend/app/schemas/property.py`
- `backend/tests/eval_set.json`
- `backend/tests/test_eval.py`
- `.ai/features/F22-search-filter-expansion/status.json`

**强制约束：**
- 新字段全部 optional，无默认值影响
- `built_year_min` 的"当前年份"使用服务端 UTC 年份，不得硬编码
- 只处理含明确数字的表达式；不处理"新楼"/"近地铁"等模糊表达
- F16 eval 30/30 不受影响
- `import app.main` exit 0

---

## T02 (Codex) — Review

只读审查，不得修改任何源文件。

---

## T03 (Claude) — Acceptance

**允许修改的文件：**
- `.ai/features/F22-search-filter-expansion/status.json`
- `.ai/features/F22-search-filter-expansion/final-report.md`
