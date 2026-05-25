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

### BUG-010 — Favorites 分页缺失 + favorite-state 上限不一致
- **Severity:** P2 · Medium
- **Status:** open
- **Source:** post-F9 smoke FAV/SRCH 测试
- **Summary:** (1) `/favorites` pageSize=12，无分页 UI，>12 条收藏不可见；(2) `/search` 请求 page_size=100 但 backend 上限 50，>50 条收藏时显示 ghost unfavorited
- **Evidence:** [results.md § BUG-010](./../qa-runs/2026-05-18-post-F9-smoke/results.md#bug-010)
- **Suggested next action:** 修复 favorites/page.tsx 分页 UI；将 search 页 getFavorites page_size 改为 ≤50 或分页获取

---

### BUG-011 — Admin 房源列表无分页
- **Severity:** P2 · Medium
- **Status:** open
- **Source:** post-F9 smoke ADMIN 测试
- **Summary:** admin/properties/page.tsx 固定 page_size=100，无分页组件；>100 条房源时数据不可访问，单次加载性能随量线性下降
- **Evidence:** [results.md § BUG-011](./../qa-runs/2026-05-18-post-F9-smoke/results.md#bug-011)
- **Suggested next action:** 为 admin 列表添加分页组件，与 properties 列表风格一致

---

### BUG-012 — Admin 表单 image_url（string）与 Property 类型 images（array）不一致
- **Severity:** P3 · Low
- **Status:** open / deferred
- **Source:** Gemini audit + post-F9 smoke
- **Summary:** property-form.tsx 使用 `image_url`（单字符串）；Property 类型期望 `images`（数组）；每次只能上传一张图，存在字段映射问题
- **Evidence:** [results.md § BUG-012](./../qa-runs/2026-05-18-post-F9-smoke/results.md#bug-012)
- **Suggested next action:** 对齐表单字段与 Property 数据模型，支持多图 URL；产品确认需求后再修

---

### BUG-014 — 注册成功后未引导用户登录
- **Severity:** P3 · Low
- **Status:** open / deferred
- **Source:** post-F9 smoke AUTH 测试 / Gemini audit NEW-010
- **Summary:** RegisterForm 注册成功后停留在 /register，显示 success message；用户需手动导航到 /login
- **Evidence:** [results.md § BUG-014](./../qa-runs/2026-05-18-post-F9-smoke/results.md#bug-014)
- **Suggested next action:** 注册成功后自动跳 /login 或直接登录跳默认页

---

### BUG-015 — ResetPasswordForm 缺少密码复杂度校验
- **Severity:** P3 · Low
- **Status:** open / deferred — 待产品决策
- **Source:** RESET-03 复测（2026-05-23）
- **Summary:** 仅校验非空、长度 ≥ 8、两次输入一致；无大小写/数字/特殊字符等复杂度要求
- **Evidence:** [fix-report BUG-008-FIX](./../qa-runs/2026-05-18-post-F9-smoke/fix-reports/fix-report-BUG-008-FIX.md)
- **Suggested next action:** 产品确认密码策略后修；不阻塞其他工作

---

## Skipped Tests

### SRCH-07 — 搜索 error state + retry 专项测试
- **Severity:** N/A · Test coverage gap
- **Status:** skipped — intentional
- **Source:** post-F9 smoke SRCH 测试
- **Summary:** 搜索出错显示 error state，retry 重新执行同一查询（URL 不变时也能重试）；本轮 backend 正常运行，未模拟错误状态
- **Evidence:** [results.md § SRCH-07](./../qa-runs/2026-05-18-post-F9-smoke/results.md)
- **Suggested next action:** 单独安排专项测试，mock backend 或断开 backend 后测试 error UI 和 retry 逻辑

---

## Backlog / Observations

### OBS-007 — 价格输入无 debounce，loading 期间阻断输入
- **Severity:** UX · Backlog
- **Status:** backlog — 待产品决策
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
