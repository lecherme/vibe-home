# Open Bug Registry

**Last updated:** 2026-05-25  
**Source run:** [post-F9 smoke results](./../qa-runs/2026-05-18-post-F9-smoke/results.md)  
**Scope:** Current open / deferred / skipped items only. Fixed BUG-001~009 not listed.

---

## Lifecycle Rules

- `open-bugs.md` only tracks current unresolved items: `open`, `in_progress`, `blocked`, `deferred`, and intentional `skipped` test gaps.
- Do not add fixed/closed historical bugs here; keep their detailed evidence in the originating QA run or feature artifact.
- When an item is fixed and verified, move it out of `open-bugs.md` to `.ai/bugs/closed-bugs.md` with:
  - fixed date
  - verifying test / QA result
  - fixing commit or feature/batch
  - link to original evidence
- Keep entries short. Use links to QA results/fix reports for detail.
- New QA runs or features should add unresolved follow-ups here during closure.

---

## Functional Bugs


## Skipped Tests


### BUG-017 — Admin 分页无直接跳页输入
- **Severity:** P3 · Low
- **Status:** backlog
- **Source:** BUG-011-FIX 复测 2026-05-25
- **Summary:** Admin 房源列表分页只有 Previous/Next，无法直接输入或点击具体页码跳转（如 "跳到第 5 页"）；数据量大时体验差
- **Suggested next action:** 在分页区加页码输入框或页码按钮列表；产品确认 UI 风格后开 fix ticket

---

## Backlog / Observations

### OBS-007 — 价格输入无 debounce，loading 期间阻断输入
- **Severity:** UX · Backlog
- **Status:** in_progress — OBS-007-FIX ticket 已创建
- **Source:** SRCH 复测 2026-05-22
- **Summary:** FilterPanel 每次 keystroke 立即触发搜索；loading 期间 disabled={isLoading} 锁死输入框。应改为 ~500ms debounce，loading 期间不阻断输入
- **Affected files:** `frontend/components/features/search/filter-panel.tsx`, `frontend/app/(dashboard)/search/page.tsx`
- **Evidence:** [results.md § OBS-007](./../qa-runs/2026-05-18-post-F9-smoke/results.md)
- **Suggested next action:** 产品确认后开 fix ticket；scope 限上述两文件

---

### OBS-008 — Bathroom 筛选缺失
- **Severity:** Feature gap · Low
- **Status:** backlog — 待产品决策
- **Source:** SRCH 复测 2026-05-22
- **Summary:** `Property` 类型有 `bathrooms` 字段，`SearchFilters` 接口和 FilterPanel 均未暴露；后端能否支持待确认
- **Evidence:** [results.md § OBS-008](./../qa-runs/2026-05-18-post-F9-smoke/results.md)
- **Suggested next action:** 确认后端搜索接口是否支持 bathrooms 参数，再决定是否加入 FilterPanel
