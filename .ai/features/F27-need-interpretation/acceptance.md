# F27 Need Interpretation Layer — Acceptance Criteria

T04 (Codex review) verifies every criterion below and writes `review.md`.
T05 (Claude acceptance) reads `review.md` and writes `final-report.md`.

---

## BUG-026 修复

| ID | Criterion |
|----|-----------|
| A1 | `_is_property_search("一室两厅")` returns True |
| A2 | `_is_property_search("一室两厅 一家三口")` returns True |
| A3 | `_is_property_search("两房一厅")` returns True |
| A4 | `_is_property_search("三室两卫")` returns True |
| A5 | `_is_property_search` 内部先做中文数字转换，pattern 匹配在转换后的字符串上进行 |
| A6 | 原有 non-search query（如"为什么房价上涨"）仍被正确拒绝 |

## living_rooms 提取

| ID | Criterion |
|----|-----------|
| A7 | `_extract_living_rooms("一室两厅")` returns 2 |
| A8 | `_extract_living_rooms("三室两厅")` returns 2 |
| A9 | `_extract_living_rooms("两室一厅")` returns 1 |
| A10 | `_extract_living_rooms("两室")` returns None（无 "厅"） |
| A11 | `interpreted_intent` 包含 `{field: "living_rooms", value: 2, filterable: False}` for "一室两厅" |
| A12 | `interpreted_intent` 中 living_rooms 的 `filterable` 为 False，不写入 SearchFilters |

## Need interpretation

| ID | Criterion |
|----|-----------|
| A13 | "一家三口" → `needs = [{type: "household_size", value: 3, raw: "一家三口"}]` |
| A14 | "一家四口" → `needs = [{type: "household_size", value: 4}]`，无 tension（与 bedrooms_min=3 无冲突） |
| A15 | "适合老人住" → `needs` 包含 `{type: "lifestyle", ...}` |
| A16 | "安静一点" → `needs` 包含 `{type: "quiet_environment", value: True, ...}` |
| A17 | "靠近好学校" → `unresolved = ["靠近好学校"]`（或类似片段）；不在 needs 中 |
| A18 | LLM 返回枚举外的 type → 该条 need 静默丢弃，其余正常 |
| A19 | `_interpret_needs` 抛异常 → `interpreted_needs` 为空默认值，搜索结果不受影响 |

## Tension detection

| ID | Criterion |
|----|-----------|
| A20 | "一室两厅 一家三口"（bedrooms_min=1, household_size=3）→ tension notice 生成："1室对3口之家可能偏小" |
| A21 | "三室两厅 一家四口"（bedrooms_min=3, household_size=4）→ 无 tension（3+1 = 4，不触发）|
| A22 | `_detect_tensions` 不调 LLM；notices 不由 `_interpret_needs` 返回 |
| A23 | bedrooms_min 为 None 时不生成 tension notice |

## API contract

| ID | Criterion |
|----|-----------|
| A24 | `AiSearchResult` 新增 `interpreted_intent` 和 `interpreted_needs` 字段，含 default 值 |
| A25 | 现有字段（parsed_filters, strict_items, recommended_items 等）不变 |
| A26 | `import app.main` exits 0 |

## Frontend

| ID | Criterion |
|----|-----------|
| A27 | `npx tsc --noEmit` exits 0 |
| A28 | tension notice 渲染为黄色（amber-50/amber-600）背景条，含 ⚠️ 图标 |
| A29 | filterable=false 的 IntentField 渲染为虚线边框 chip，含"（暂无数据）"标注 |
| A30 | needs raw 表达渲染为灰色小标签 |
| A31 | unresolved 渲染为浅灰色小字提示 |
| A32 | 所有字段为空时不渲染任何 UI 元素 |
| A33 | 不引入 shadcn 组件；使用 Tailwind class 实现 |

## Evaluation

| ID | Criterion |
|----|-----------|
| A34 | `eval_set_f27.json` 包含 ≥8 条 query，覆盖所有 spec case 类型 |
| A35 | BUG-026 回归测试：`一室两厅` 类 query 正确进入搜索管道 |
| A36 | tension 检测断言：household_size=3 + bedrooms_min=1 → tension notice 存在 |

## Non-regression

| ID | Criterion |
|----|-----------|
| A37 | F16 eval 30/30 不变（`bash tools/run_eval.sh`） |
| A38 | `_parse_filters` source 未改动 |
| A39 | `_relax_filters` / `_apply_relaxation` source 未改动 |

---

## Review and Acceptance

If review verdict is FAIL, Claude does NOT proceed directly to T05 acceptance.
Claude must:
1. Write `last_review_failure` to `status.json` with fix_path, failed_criteria, and fix_instructions.
2. Choose fix_path: task_retry, direct_fixup, or review_rerun.
3. Apply the fix and re-run review before acceptance.

## Rejection Conditions

- Any task modifies files outside its ownership boundary.
- Any worker modifies `status.json`.
- Any required artifact is missing or malformed.
- `_detect_tensions` calls LLM.
- `living_rooms` is written into `SearchFilters`.
