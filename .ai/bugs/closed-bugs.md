# Closed Bug Registry

Resolved items moved from `open-bugs.md`.

Each entry should include fixed date, verification evidence, fixing commit/batch, and original source link.

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

### BUG-016 — Root route / 显示 HealthPage 而非角色跳转

- **Fixed date:** 2026-05-25
- **Verification:** tsc exit 0；手动复测 PASS — 未登录/user/admin 访问 `/` 均正确跳转；`/health` 正常显示
- **Fixing batch:** `.ai/fix-runs/2026-05-24-post-F9-followup` — BUG-016-FIX
- **Fix:** middleware 在 `if(session)` 块内加 `pathname === "/"` 跳转到 `getDefaultPage(role)`；`app/page.tsx` 改为 `redirect("/login")` 兜底；原 HealthPage 迁移到 `app/health/page.tsx`
- **Original source:** [open-bugs.md § BUG-016](./../bugs/open-bugs.md)（已移除）
- **Fix report:** [fix-report-BUG-016-FIX](./../fix-runs/2026-05-24-post-F9-followup/fix-reports/fix-report-BUG-016-FIX.md)
