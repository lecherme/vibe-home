# F26 Trusted Search — Ownership Boundaries

---

## T01 (Codex) — Backend contract + constraint fixes

**允许修改的文件：**
- `backend/app/schemas/ai_search.py`
- `backend/app/services/ai_search/service.py`

**在 `service.py` 内，允许修改或新增：**
- `_relax_filters` — 移除 `bedrooms_min` / `bathrooms_min` 逻辑；新增 `subway_distance_max` 和 `built_year_min` 放宽逻辑
- `_resolve_result_ids` — 替换为 hybrid score fusion
- `ai_search` — 生成 `strict_items`, `recommended_items`, `relaxations`, `parsed_constraints`, `match_reasons`
- 新增辅助函数：`_matches_hard_constraints`, `_build_match_reasons`, `_build_parsed_constraints`

**在 `service.py` 内，不得修改的函数：**
- `_parse_filters`
- `_is_property_search`
- `_generate_summary`
- `_apply_relaxation`
- `_apply_subjective_room_filters`
- `_normalize_query`

**不得修改：**
- `backend/app/schemas/search.py`
- `backend/app/services/search/service.py`
- `backend/tests/eval_set.json`
- `backend/tests/test_eval.py`
- 任何 frontend 文件
- `.ai/features/F26-trusted-search/status.json`

**强制约束：**
- `match_reasons` 必须由确定性代码生成，不得调用 LLM
- `items` = `strict_items + recommended_items`，strict 在前
- `total` = len(strict_items) + len(recommended_items)
- `parsed_filters` 继续保留原始 intent（BUG-025 非回归）
- F16 eval 30/30 不受影响
- `import app.main` exit 0

---

## T02 (Codex) — Frontend rendering

**允许修改的文件：**
- `frontend/components/features/search/ai-parsed-filters-card.tsx`
- `frontend/components/features/search/ai-search-results.tsx`（新建或修改）
- `frontend/components/features/search/match-reasons-chips.tsx`（新建）
- `frontend/components/features/search/relaxation-notice.tsx`（新建）
- `frontend/app/(dashboard)/search/page.tsx`
- `frontend/types/ai-search.ts`（新建或修改）

**不得修改：**
- 任何 backend 文件
- `frontend/components/features/search/filter-panel.tsx`
- `frontend/components/features/search/search-bar.tsx`
- `.ai/features/F26-trusted-search/status.json`

**强制约束：**
- `match_reasons` chips 不得由前端自行推断；必须从 API 响应消费
- 当 `recommended_items` 为空时，不渲染推荐区
- `npx tsc --noEmit` exit 0

---

## T03 (Codex) — Evaluation set

**允许修改的文件：**
- `backend/tests/eval_set_f26.json`（新建）
- `backend/tests/test_eval_f26.py`（新建）

**不得修改：**
- `backend/tests/eval_set.json`
- `backend/tests/test_eval.py`
- 任何 source 文件
- `.ai/features/F26-trusted-search/status.json`

**强制约束：**
- ≥10 条 query，覆盖 spec 中规定的全部 case 类型
- 测试断言必须包含：hard-filter precision、strict/recommended split、relaxation correctness
- `bash tools/run_eval.sh` (F16) 仍 30/30

---

## T04 (Codex) — Review

只读审查，不得修改任何源文件。

---

## T05 (Claude) — Acceptance

**允许修改的文件：**
- `.ai/features/F26-trusted-search/status.json`
- `.ai/features/F26-trusted-search/final-report.md`
