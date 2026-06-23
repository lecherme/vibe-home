# F27 Need Interpretation Layer — Ownership Boundaries

---

## T01 (Codex) — Backend + BUG-026 + frontend types

**允许修改的文件：**
- `backend/app/schemas/ai_search.py`
- `backend/app/services/ai_search/service.py`
- `frontend/types/ai-search.ts`
- `.ai/features/F27-need-interpretation/tension-policy.md`（新建）

**在 `service.py` 内，允许修改或新增：**
- `_is_property_search` — 入口处加中文数字转换 + 补 `厅` pattern（BUG-026）
- `_LIVING_ROOM_PATTERN` — 新增模块级常量
- `_extract_living_rooms` — 新增
- `_interpret_needs` — 新增
- `_detect_tensions` — 新增
- `ai_search` — 插入 living_rooms 提取 + need interpretation 调用

**在 `service.py` 内，不得修改的函数：**
- `_parse_filters`（及其内部所有子函数）
- `_relax_filters` / `_apply_relaxation`
- `_resolve_result_ids`
- `_generate_summary`
- `_build_match_reasons`
- `_build_parsed_constraints`
- `_normalize_query`
- `_keyword_fallback_search`

**不得修改：**
- `backend/app/schemas/search.py`
- `backend/app/services/search/service.py`
- `backend/tests/eval_set.json`
- `backend/tests/test_eval.py`
- 任何 frontend 组件文件
- `.ai/features/F27-need-interpretation/status.json`

**强制约束：**
- `notices` 必须由 `_detect_tensions` Python 代码生成，不得由 LLM 输出
- `_interpret_needs` 调用必须在独立 try/except 中，失败不影响搜索结果
- `living_rooms` 不得写入 `SearchFilters`（filterable=False）
- `import app.main` exit 0
- `npx tsc --noEmit` exit 0

---

## T02 (Gemini) — Frontend UI rendering

**允许修改的文件：**
- `frontend/components/features/search/interpreted-needs-card.tsx`（新建）
- `frontend/app/(dashboard)/search/page.tsx`

**不得修改：**
- 任何 backend 文件
- `frontend/types/ai-search.ts`（T01 已完成）
- `frontend/components/features/search/ai-parsed-filters-card.tsx`
- `frontend/components/features/search/ai-search-results.tsx`
- `frontend/components/features/search/match-reasons-chips.tsx`
- `frontend/components/features/search/relaxation-notice.tsx`
- `.ai/features/F27-need-interpretation/status.json`

**强制约束：**
- 不使用 shadcn 组件；使用 Tailwind class 实现
- `filterable=false` 的 IntentField → 虚线边框 chip + "（暂无数据）"标注
- 全部字段为空时不渲染任何 UI 元素
- `npx tsc --noEmit` exit 0

---

## T03 (Codex) — Evaluation set

**允许修改的文件：**
- `backend/tests/eval_set_f27.json`（新建）
- `backend/tests/test_eval_f27.py`（新建）

**不得修改：**
- `backend/tests/eval_set.json`
- `backend/tests/eval_set_f26.json`
- `backend/tests/test_eval.py`
- `backend/tests/test_eval_f26.py`
- 任何 source 文件
- `.ai/features/F27-need-interpretation/status.json`

**强制约束：**
- ≥8 条 query，覆盖 spec 中规定的全部 case 类型
- 必须包含 BUG-026 回归测试：`一室两厅` 进入搜索管道
- 必须包含 living_rooms 提取、tension 检测、unresolved 保留断言

---

## T04 (Codex) — Review

只读审查，不得修改任何源文件。

---

## T05 (Claude) — Acceptance

**允许修改的文件：**
- `.ai/features/F27-need-interpretation/status.json`
- `.ai/features/F27-need-interpretation/final-report.md`
