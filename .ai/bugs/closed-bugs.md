# Closed Bug Registry

Resolved items moved from `open-bugs.md`.

Each entry should include fixed date, verification evidence, fixing commit/batch, and original source link.

---

### BUG-019 — /properties page 收藏状态上限遗漏

- **Fixed date:** 2026-05-31
- **Verification:** tsc exit 0；手动复测 PASS — 列表加载正常，收藏/取消收藏 heart 状态正常，分页正常
- **Fixing batch:** `.ai/fix-runs/2026-05-24-post-F9-followup` — BUG-019-FIX
- **Fix:** `properties/page.tsx` 将 `favoritesApi.getFavorites(1, 100)` 替换为 `favoritesApi.getAllFavoriteIds().catch(() => new Set<string>())`；`.then()` 直接使用返回的 Set，不再做 items 映射；超过 50 条收藏时状态完整
- **Original source:** Gemini 二次审查发现（2026-05-31）

---

### BUG-018 — Admin properties table overlaps on tablet/narrow viewport

- **Fixed date:** 2026-05-28
- **Verification:** tsc exit 0；手动复测 iPad viewport PASS — 列不再重叠，窄屏横向滚动正常，title/location truncate 生效
- **Fixing batch:** `.ai/fix-runs/2026-05-24-post-F9-followup` — BUG-018-FIX
- **Fix:** table `min-w-[1024px]`；Property `<th>` `w-64`；Property/Location `<td>` 改用 `max-w-0` + `truncate`，去掉 `whitespace-nowrap`；`overflow-x-auto` 保留
- **Original source:** PAGINATION-UX-FIX 手测 2026-05-28
- **Fix report:** [fix-report-BUG-018-FIX](./../fix-runs/2026-05-24-post-F9-followup/fix-reports/fix-report-BUG-018-FIX.md)

---

### BUG-017 / PAGINATION-UX — 全部列表页分页缺少直接跳页能力

- **Fixed date:** 2026-05-28
- **Verification:** tsc exit 0；手动复测 PASS — PaginationControls 在 /properties、/search、/favorites、/admin/properties 均显示；Enter/Go 跳页行为一致；超范围 clamp 正确；URL sync 正常
- **Fixing batch:** `.ai/fix-runs/2026-05-24-post-F9-followup` — PAGINATION-UX-FIX
- **Fix:** 新建 `PaginationControls` 共享组件（Previous/Next/Go-to-page，noValidate + 手写 clamp）；替换 4 个页面的重复分页 JSX；各页面 URL sync 逻辑不变
- **Original source:** BUG-011-FIX 复测 2026-05-25
- **Fix report:** [fix-report-PAGINATION-UX-FIX](./../fix-runs/2026-05-24-post-F9-followup/fix-reports/fix-report-PAGINATION-UX-FIX.md)

---

### BUG-013 — 生产环境 API URL 无 fallback，部署风险

- **Fixed date:** 2026-05-24
- **Verification:** tsc exit 0；`grep -r "NEXT_PUBLIC_API_URL" frontend/lib/api/` 仅 config.ts 一处；`grep -r "localhost:8000" frontend/lib/api/` 无残留
- **Fixing batch:** `.ai/fix-runs/2026-05-24-post-F9-followup` — BUG-013-FIX
- **Fix:** 新建 `frontend/lib/api/config.ts` 统一导出 `apiUrl`，缺省时 throw `"NEXT_PUBLIC_API_URL is not configured"`；5 个 api 文件改为 import from config.ts
- **Original source:** [post-F9 smoke results § BUG-013](./../qa-runs/2026-05-18-post-F9-smoke/results.md)
- **Fix report:** [fix-report-BUG-013-FIX](./../fix-runs/2026-05-24-post-F9-followup/fix-reports/fix-report-BUG-013-FIX.md)

---

### BUG-014 — 注册成功后未引导用户登录

- **Fixed date:** 2026-05-27
- **Verification:** tsc exit 0；手动复测 PASS — 3 秒自动跳 /login，Back to Login 立即跳转
- **Fixing batch:** `.ai/fix-runs/2026-05-24-post-F9-followup` — BUG-014-FIX
- **Fix:** RegisterForm 注册成功后用 useEffect 启动 3 秒 timer → router.push("/login")；保留 Back to Login 链接；unmount 时清理 timer
- **Original source:** [results.md § BUG-014](./../qa-runs/2026-05-18-post-F9-smoke/results.md#bug-014)
- **Fix report:** [fix-report-BUG-014-FIX](./../fix-runs/2026-05-24-post-F9-followup/fix-reports/fix-report-BUG-014-FIX.md)

---

### BUG-012 — Admin 表单 image_url 与 Property.images 不一致

- **Fixed date:** 2026-05-26
- **Verification:** tsc exit 0；Python import exit 0；手动复测 PASS — 新增多图、编辑保留多图、Remove disabled
- **Fixing batch:** `.ai/fix-runs/2026-05-24-post-F9-followup` — BUG-012-FIX
- **Fix:** 后端 schema 改为 `images: list[str]`，删除 `_build_images()` 适配器；前端类型和表单对齐，动态 URL 列表（最多 5 个）；编辑页加载改为 `property.images ?? []`
- **Original source:** [results.md § BUG-012](./../qa-runs/2026-05-18-post-F9-smoke/results.md#bug-012)
- **Fix report:** [fix-report-BUG-012-FIX](./../fix-runs/2026-05-24-post-F9-followup/fix-reports/fix-report-BUG-012-FIX.md)

---

### BUG-010 — Favorites 分页缺失 + ghost unfavorited

- **Fixed date:** 2026-05-26
- **Verification:** tsc exit 0；手动复测 PASS — /favorites 分页、URL params 刷新保页、取消收藏边界；/search 收藏同步回归 PASS
- **Fixing batch:** `.ai/fix-runs/2026-05-24-post-F9-followup` — BUG-010-FIX
- **Fix:** 新增 `getAllFavoriteIds()` 循环翻页（page_size=50）取全量收藏 ID；search 页改用该 helper 并静默降级；favorites 页加 PAGE_SIZE=12 分页 + URL params 同步 + 取消收藏边界逻辑
- **Original source:** [results.md § BUG-010](./../qa-runs/2026-05-18-post-F9-smoke/results.md#bug-010)
- **Fix report:** [fix-report-BUG-010-FIX](./../fix-runs/2026-05-24-post-F9-followup/fix-reports/fix-report-BUG-010-FIX.md)

---

### BUG-011 — Admin 房源列表无分页

- **Fixed date:** 2026-05-25
- **Verification:** tsc exit 0；手动复测 PASS — 分页控件、URL params 刷新保页、Actions 列完整显示、边界删除无空状态闪烁
- **Fixing batch:** `.ai/fix-runs/2026-05-24-post-F9-followup` — BUG-011-FIX
- **Fix:** 新增 PAGE_SIZE=20 分页逻辑；page 同步 URL `?page=N`；table-fixed 布局固定 Actions 列宽；边界删除保持 deleting 状态直到跳页
- **Original source:** [results.md § BUG-011](./../qa-runs/2026-05-18-post-F9-smoke/results.md#bug-011)
- **Fix report:** [fix-report-BUG-011-FIX](./../fix-runs/2026-05-24-post-F9-followup/fix-reports/fix-report-BUG-011-FIX.md)

---

### OBS-008 — Bathroom 筛选缺失

- **Fixed date:** 2026-05-28
- **Verification:** tsc exit 0；backend import exit 0；手动复测 PASS — Min Bathrooms select 正确显示，N+ 语义过滤生效，URL param 同步，Clear Filters / back-forward 均正常，组合筛选正常
- **Fixing batch:** `.ai/fix-runs/2026-05-24-post-F9-followup` — OBS-008-FIX
- **Fix:** 全栈补全 bathrooms 筛选：backend schema/router/service（N+ 语义，ge=0）；frontend types/api/search-page/filter-panel（Min Bathrooms select，1–5，N+ baths）
- **Original source:** [results.md § OBS-008](./../qa-runs/2026-05-18-post-F9-smoke/results.md)
- **Fix report:** [fix-report-OBS-008-FIX](./../fix-runs/2026-05-24-post-F9-followup/fix-reports/fix-report-OBS-008-FIX.md)

---

### OBS-007 — 价格输入无 debounce，loading 期间阻断输入

- **Fixed date:** 2026-05-27
- **Verification:** tsc exit 0；手动复测 PASS — 500ms debounce 生效，切换 bedrooms 时 price 不被清空，Clear Filters 正常，loading 期间 inputs 锁住
- **Fixing batch:** `.ai/fix-runs/2026-05-24-post-F9-followup` — OBS-007-FIX
- **Fix:** `filter-panel.tsx` 为 min/max price 引入 local state + 500ms debounce；useEffect guard 防止 typing 期间被其他 filter 变化覆盖；保留 `disabled={isLoading}` 避免并发请求 race condition（OBS-010 记录到 next-iteration）。`search/page.tsx` overlay 加 `pointer-events-none`
- **Original source:** [results.md § OBS-007](./../qa-runs/2026-05-18-post-F9-smoke/results.md)
- **Fix report:** [fix-report-OBS-007-FIX](./../fix-runs/2026-05-24-post-F9-followup/fix-reports/fix-report-OBS-007-FIX.md)

---

### SRCH-07 — 搜索 error state + retry 专项测试

- **Fixed date:** 2026-05-27
- **Verification:** 手动测试 PASS — `docker compose stop backend` 后搜索显示 fetch error banner；Retry 重新执行同一查询（URL params 不变）；backend 恢复后正常展示结果
- **Fixing batch:** N/A — 纯测试，无代码变更
- **Fix:** 无需修复，功能正确
- **UX observation:** 错误状态下旧列表仍保留但无 stale 标注，返回后旧列表消失；记录为 OBS-009，进入 next-iteration backlog
- **Original source:** [results.md § SRCH-07](./../qa-runs/2026-05-18-post-F9-smoke/results.md)

---

### BUG-015 — ResetPasswordForm / RegisterForm 缺少密码复杂度校验

- **Fixed date:** 2026-05-27
- **Verification:** tsc exit 0；RegisterForm 手动复测 PASS — 弱密码各分支均拦截，`Password1` 通过；ResetPasswordForm 手动复测 PASS — 弱密码拦截、强密码修改成功、跳 `/login`、新密码登录成功
- **Fixing batch:** `.ai/fix-runs/2026-05-24-post-F9-followup` — BUG-015-FIX
- **Fix:** 新建 `frontend/lib/auth/password-validation.ts` 导出 `validatePassword()`（长度 ≥ 8、小写、大写、数字）；RegisterForm 在 confirmPassword 校验前插入；ResetPasswordForm 替换原长度单一检查
- **Original source:** [post-F9 smoke results § BUG-015](./../qa-runs/2026-05-18-post-F9-smoke/results.md)
- **Fix report:** [fix-report-BUG-015-FIX](./../fix-runs/2026-05-24-post-F9-followup/fix-reports/fix-report-BUG-015-FIX.md)

---

### BUG-016 — Root route / 显示 HealthPage 而非角色跳转

- **Fixed date:** 2026-05-25
- **Verification:** tsc exit 0；手动复测 PASS — 未登录/user/admin 访问 `/` 均正确跳转；`/health` 正常显示
- **Fixing batch:** `.ai/fix-runs/2026-05-24-post-F9-followup` — BUG-016-FIX
- **Fix:** middleware 在 `if(session)` 块内加 `pathname === "/"` 跳转到 `getDefaultPage(role)`；`app/page.tsx` 改为 `redirect("/login")` 兜底；原 HealthPage 迁移到 `app/health/page.tsx`
- **Original source:** [open-bugs.md § BUG-016](./../bugs/open-bugs.md)（已移除）
- **Fix report:** [fix-report-BUG-016-FIX](./../fix-runs/2026-05-24-post-F9-followup/fix-reports/fix-report-BUG-016-FIX.md)
