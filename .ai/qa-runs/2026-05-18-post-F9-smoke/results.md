# QA Run: 2026-05-18 Post-F9 Smoke

**Date:** 2026-05-18  
**Tester:** Manual (QA lead: Claude)  
**Branch/Commit:** `b7a9803` — feat(F9-frontend-ux-polish): checkpoint at T08_done — ACCEPTED  
**Environment:** localhost — frontend :3000 / backend :8000 / docker compose  
**Scope:** Post-F9 smoke — security, route protection, auth, search, favorites, admin, password reset  

---

## 环境快照

| 项目 | 状态 |
|------|------|
| frontend container | Up |
| backend container | Up (healthy) |
| GET /login (3000) | 200 |
| GET /health (8000) | 200 |

---

## 结果记录

### Section 13 — Security Checks（优先）

| ID | 描述 | Status | Evidence | Notes |
|----|------|--------|----------|-------|
| SEC-01 | 登录表单提交后 email/password 不出现在 URL | **PASS** | 复测：URL 保持 `/login`，凭据发往 `supabase.co/auth/v1/token?grant_type=password`，不出现在 URL | BUG-001-FIX 有效 |
| SEC-02 | 登录凭据不出现在 browser history | **PASS** | 复测：browser history 仅记录 `/login`，无 query string 凭据 | BUG-001-FIX 有效 |
| SEC-03 | 登录凭据不出现在 Docker logs | **PASS** | 复测：frontend log 仅 `GET /login 200` → `GET /properties 200`，无凭据出现；auth 直接走 Supabase，不经 Next.js server | |
| SEC-04 | network tab 显示凭据在 POST body，不在 URL params | **PASS** | 复测：凭据在 POST body 发往 Supabase（`grant_type=password, email, password`），URL 干净 | |
| SEC-05 | redirectTo 不能跳转到外部域名 | **PASS** | 已登出访问 `/login?redirectTo=https://evil.com`，登录后落到 `/properties`，未跳转外部域 | LoginForm L12 验证正确拒绝非相对路径 |

### Section 1 — Route Protection & redirectTo

| ID | 描述 | Status | Evidence | Notes |
|----|------|--------|----------|-------|
| AUTH-01 | 未登录访问 /properties → /login?redirectTo=/properties | **PASS** | 重定向到 `/login?redirectTo=%2Fproperties` | |
| AUTH-02 | 未登录访问 /search → /login?redirectTo=/search | **PASS** | 重定向到 `/login?redirectTo=%2Fsearch` | |
| AUTH-03 | 未登录访问 /favorites → /login?redirectTo=/favorites | **PASS** | 重定向到 `/login?redirectTo=%2Ffavorites` | |
| AUTH-04 | 未登录访问 /admin/properties → 拒绝或重定向 | **PASS** | 重定向到 `/login?redirectTo=%2Fadmin%2Fproperties` | |
| AUTH-05 | 已登录访问 /login → 跳离 auth 页 | **FAIL** | 已登录访问 `/login?redirectTo=https://evil.com` → 落到 `http://192.168.31.136:3000`（根路由 HealthPage） | middleware 踢出 /login 时 redirect 目标是 `/` 而非 `/properties`，BUG-003 同一根因 |
| AUTH-06 | 已登录访问 /register → 跳离 auth 页 | **FAIL** | 已登录访问 `/register` → 落到 `http://192.168.31.136:3000`（根路由 HealthPage） | 跳离 auth 页✓，但落点是 `/` 而非 `/properties`，BUG-003 同一根因 |

### Section 2 — Authentication（login/logout/redirectTo 回跳）

| ID | 描述 | Status | Evidence | Notes |
|----|------|--------|----------|-------|
| AUTH-07 | 有效账户登录成功 | **PASS** | 登录后跳转到 `/properties` | |
| AUTH-08 | 登录后回跳到 redirectTo 原始路由 | **PASS** | `/login?redirectTo=%2Fsearch` 登录后落到 `/search`，页面内容正常（含搜索条件栏和搜索按钮） | |
| AUTH-09 | 无 redirectTo 时落地 /properties | **PASS** | 与 AUTH-07 同测，落点 `/properties` | |
| AUTH-10 | 登录失败显示错误，表单可继续使用 | **PASS** | 错误密码显示 "Invalid login credentials"；重新填写正确密码后登录成功跳转 `/properties` | |
| AUTH-11 | Sign out 清除 session，跳转 /login | **PASS** | Sign out 后跳转到 `/login` | |
| AUTH-12 | 登出后 browser back 不能回到保护页面 | **PASS** | 登出后按 back → 落到 `/login?redirectTo=%2Fproperties`，未直接进入 `/properties` | middleware 拦截成功 |
| AUTH-13 | 注册：密码不一致显示错误 | **PASS** | 显示 "Passwords do not match" | |

### Section 5 — Search URL State + Clear Filters + Retry

| ID | 描述 | Status | Evidence | Notes |
|----|------|--------|----------|-------|
| SRCH-01 | /search 无筛选加载结果 | **PASS** | 无筛选条件下正常加载房源列表 | 搜索字段：Min Price、Max Price（input）；Min Bedrooms、Status（select）|
| SRCH-02 | location 搜索更新 URL + 结果 | **PASS** | location 框回车和点搜索按钮均可触发搜索，URL 同步更新 | location 字段样式不显眼（UX 观察，非阻断）|
| SRCH-03 | 筛选参数持久化到 URL query string | **PASS** | 筛选参数同步到 URL | **UX 观察：** Min Price 每次变动即触发搜索（非点搜索按钮后触发），体验待产品决策：是预期的 live-search 还是应改为 debounce/on-submit |
| SRCH-04 | Clear filters 重置 URL + 结果，不需手动再点 Search | **FAIL** | 页面未见 Clear filters / 重置按钮 | 功能缺失或 UI 未暴露入口 |
| SRCH-05 | 搜索分页保留 active filters | **PASS** | 翻页后 URL 筛选参数保留 | |
| SRCH-06 | browser back/forward 保持表单状态与结果同步 | **PASS** | 前进后退时 URL 和搜索结果同步 | |
| SRCH-07 | 搜索出错显示 error state，retry 重新执行同一查询（URL 不变时也能重试） | **SKIPPED** | 后端正常运行，本轮不强行模拟错误状态 | 后续用 mock/断 backend 单独测 |

### Section 6 — Favorites Add/Remove

> **观察（待验证）：** 收藏按钮疑似乐观更新，点击后 UI 立即变化。FAV-01~05 测试时重点确认：请求期间是否有 loading 状态、失败是否回滚、409 是否静默处理。若不符合产品预期（等真实请求后再更新）则开 bug。

| ID | 描述 | Status | Evidence | Notes |
|----|------|--------|----------|-------|
| FAV-01 | 列表页可添加收藏 | **PASS** | 点击后图标变化，收藏成功 | UX 观察：可操作时 cursor 为手形，请求期间为默认指针（loading 反馈通过 cursor 体现，疑似乐观更新待确认）|
| FAV-02 | 列表页可取消收藏 | **PASS** | 再次点击取消收藏，图标恢复 | |
| FAV-03 | 详情页可添加收藏 | **PASS** | 详情页收藏功能正常 | |
| FAV-04 | 详情页可取消收藏 | **PASS** | 详情页取消收藏功能正常 | |
| FAV-05 | 重复收藏不破坏 UI（409 静默处理） | **PASS** | 快速连点 2~3 次无异常、无报错 | |
| FAV-06 | /favorites 页列出已收藏房源 | **PASS** | 收藏后访问 `/favorites` 房源正常显示 | **跨 tab 同步观察：** 另一窗口取消收藏后，/favorites 页不自动更新；刷新后才反映最新状态 |
| FAV-07 | 从 /favorites 页移除收藏后卡片消失 | **PASS** | 卡片移除后消失，功能正确 | UX 观察：无移除动效/过渡动画，卡片瞬间消失 |

### Section 8 — Admin Create/Edit/Delete

| ID | 描述 | Status | Evidence | Notes |
|----|------|--------|----------|-------|
| ADMIN-01 | admin 用户可访问 /admin/properties | **PASS** | BUG-005-FIX 后，`victorxzf@gmail.com` 重新登录后可正常访问 `/admin/properties`，列表显示正常 | BUG-005-FIX 有效 |
| ADMIN-02 | 非 admin 用户被拦截 | **PASS** | `coolhorse@qq.com` 访问 `/admin/properties` → 重定向到 `http://192.168.31.136:3000`（HealthPage） | 拦截正确；落点为 `/` 是 BUG-003 已知问题 |
| ADMIN-03 | 填写表单创建新房源 | **PASS** | BUG-006-FIX 后，创建房源保存成功 | |
| ADMIN-04 | 新建房源出现在公开列表 | **PASS** | 新建房源在 `/properties` 列表可见；admin 在该页可见收藏控件并触发 HTTP 403，见 BUG-007 | |
| ADMIN-05 | 编辑已有房源，保存后变更可见 | **PASS** | 编辑保存后变更正常显示 | |
| ADMIN-06 | 取消删除确认不改变数据 | **PASS** | 点删除 → 取消确认 → 数据不变 | |
| ADMIN-07 | 确认删除后房源从列表消失 | **PASS** | 确认删除后房源正常消失 | |

### Section 12 — Password Reset（Known Issue）

| ID | 描述 | Status | Evidence | Notes |
|----|------|--------|----------|-------|
| RESET-01 | /login 页有 "Forgot password" 入口 | **FAIL** | `/login` 页面无 "Forgot password" 或任何密码重置入口 | 功能缺失 |
| RESET-02 | 提交 reset 请求后显示确认提示 | **BLOCKED** | 阻塞于 RESET-01，无入口可测 | |
| RESET-03 | 点击邮件中 reset 链接打开 reset 表单 | **BLOCKED** | 已知问题：reset 链接打不开 | 待修复后验证 |

---

## Bug 记录

### BUG-001 — LoginForm GET 凭据泄露（P0 · Blocker）

- **ID:** BUG-001
- **Flow:** Authentication
- **Page/route:** `/login`
- **User role:** any
- **Steps to reproduce:** 在登录表单填写 email + password，点击 Sign in
- **Actual result:** URL 变为 `/login?email=<email>&password=<password>`，凭据明文出现在 URL、browser history、server access log
- **Expected result:** 凭据通过 POST body 提交，URL 不变（保持 `/login` 或跳转目标页）
- **Root cause:** `LoginForm.tsx` 的 `<form>` 缺少 `method="post"`，默认 GET；若 JS 未能拦截 `onSubmit`（或提交早于 JS hydration），凭据进 query string
- **Console/network error:** 无 JS 错误；Network tab 显示 GET 请求，无 Request Body
- **Severity:** blocker
- **Status:** fix applied — 见 BUG-001-FIX-1；regression → BUG-002（已关闭）
- **Related:** SEC-01 / SEC-02 / SEC-03 / SEC-04 全部因此 FAIL；在 F9 启动前已发现（知情搁置）
- **Fix notes (BUG-001-FIX):** `LoginForm.tsx` L39 加 `method="post"`；`login/page.tsx` 加 `Suspense` 包裹；tsc exit 0

---

### BUG-002 — 登录行为异常（closed）

- **ID:** BUG-002
- **Flow:** Authentication
- **Page/route:** `/login`
- **User role:** any
- **Steps to reproduce:** 含 BUG-001-FIX 的代码状态下，从 LAN IP 访问 `/login`，填写账户，点击 Sign in
- **Original symptom:** 登录点击后无反应，Network 显示原生 form POST 到 Next.js 页面（`POST /login?redirectTo=/ 200`）
- **Root cause（修正）:** onSubmit **已接管**（stack 确认 `LoginForm.tsx:25` 已执行）；原始症状为三个环境配置问题叠加：
  1. `allowedDevOrigins` 未配置 → HMR/dev resource 从 LAN IP 被 block
  2. `NEXT_PUBLIC_API_URL=http://localhost:8000` → 浏览器端 API 请求打到客户端本机（ERR_CONNECTION_REFUSED）
  3. `backend/.env` CORS 未含 LAN origin → API 请求被 block
- **Severity:** blocker（环境配置问题，非业务代码 bug）
- **Status:** **closed** — 三项环境配置修复后登录功能恢复
- **Fix notes (BUG-002-FIX-1):**
  - Gemini worker ECONNRESET exit 1，partial patch 配置层级错误（写入 `experimental.allowedDevOrigins`）
  - Claude fallback（已授权）：修正为顶层 `allowedDevOrigins`，仅改 `frontend/next.config.mjs`
  - `frontend/.env`：`NEXT_PUBLIC_API_URL` → `http://192.168.31.136:8000`（直接修复，未走 worker）
  - `backend/.env`：`ALLOWED_ORIGINS` / `CORS_ALLOWED_ORIGINS` 加入 `http://192.168.31.136:3000`（直接修复，force-recreate 容器生效）
- **Related:** BUG-003（登录后落错页，独立 bug）

---

### BUG-003 — redirectTo=/ 登录后落到 HealthPage（P1 · High）

- **ID:** BUG-003
- **Flow:** Authentication / redirectTo
- **Page/route:** `/login?redirectTo=/`
- **User role:** any authenticated
- **Steps to reproduce:** 访问 `/login?redirectTo=/`，填写有效账户，登录
- **Actual result:** 登录成功后 `router.push("/")` → 落到 HealthPage，而非 `/properties`
- **Expected result（产品决策 2026-05-18）:**
  - 无 `redirectTo`：普通用户 → `/properties`；admin → `/admin/properties`
  - 有合法 `redirectTo`（非 `/`）：优先回跳原始路由
  - `redirectTo=/`：视为无 `redirectTo`，按角色落到默认首页（不落 HealthPage）
  - `/favorites` 不作为任何角色的默认首页
- **Root cause:** `LoginForm.tsx` L12 验证逻辑：`raw.startsWith("/") && !raw.startsWith("//")` — `"/"` 通过验证被视为合法 redirectTo，但 `/` 是 HealthPage；middleware 对未登录访问根路由 `/` 生成 `redirectTo=/`，触发此路径
- **Severity:** high（登录后落错页，非 blocker）
- **Status:** open — 不修，待授权
- **附加影响:** 根路由 `/`（HealthPage）无 Sign Out 按钮和导航入口，用户落到此页后需手动导航到 `/properties` 才能登出；BUG-003 修复后复评

---

### BUG-004 — /search 无 Clear Filters 入口（P2 · Medium）

- **ID:** BUG-004
- **Flow:** Search
- **Page/route:** `/search`
- **User role:** any authenticated
- **Steps to reproduce:** 填写任意筛选条件后，寻找重置/清除按钮
- **Actual result:** 页面未见 Clear filters / 重置按钮
- **Expected result:** 应有 Clear filters 入口，点击后重置 URL 参数并自动刷新结果（无需再点搜索）
- **Severity:** medium
- **Status:** open — 不修，待授权

---

### BUG-005 — Admin role claim mismatch（P0 · Blocker）

- **ID:** BUG-005
- **Flow:** Admin access control
- **Page/route:** `/admin/properties`
- **User role:** admin
- **Steps to reproduce:** 将账户 `app_metadata` 设为 `{"app_role": "admin"}`，登录后访问 `/admin/properties`
- **Actual result:** 重定向到 `/`（HealthPage），admin 无法进入管理页面
- **Expected result:** admin 用户可正常访问 `/admin/properties`
- **Root cause:** `frontend/middleware.ts` 读取 `decodeJwtPayload(token)?.app_role`（JWT 顶层），但 Supabase 默认将自定义 claim 存入 `app_metadata`，实际 JWT 结构为 `payload.app_metadata.app_role`；两者路径不一致导致 middleware 始终读到 `undefined`，将所有用户视为非 admin
- **Fix directions:**
  - **短期（推荐）：** 改 `middleware.ts`，读取 `payload.app_metadata?.app_role`
  - **长期：** 配置 Supabase custom access token hook，在 JWT 顶层注入 `app_role` claim
- **Severity:** blocker（admin 功能完全不可用）
- **Status:** **fixed** — BUG-005-FIX 已应用（2026-05-21）；ADMIN-01 手动复测 PASS
- **Related:** ADMIN-01 复测 PASS；BUG-006（backend 同病，已修）

---

### BUG-006 — 后端 admin role claim mismatch（P0 · Blocker）

- **ID:** BUG-006
- **Flow:** Admin CRUD（create / edit / delete）
- **Page/route:** `/admin/properties`
- **User role:** admin
- **Steps to reproduce:** 以 admin 身份登录，在 `/admin/properties` 创建、编辑或删除房源
- **Actual result:** 所有写操作返回 `HTTP 403: Insufficient permissions`；错误来源 `lib/api/admin.ts:77`（AdminApiError），后端 `require_role("admin")` 拒绝请求
- **Expected result:** admin 用户可正常执行创建、编辑、删除操作
- **Root cause:** `backend/app/core/security.py` 从 JWT payload 读取顶层 `app_role` 字段；但 Supabase 默认将自定义 claim 存入 `app_metadata`，实际路径为 `payload["app_metadata"]["app_role"]`；后端始终读到 `None`，fallback 为 `"user"` role，触发 403
- **Fix direction:** 改 `security.py` 中 role 提取逻辑，支持 `payload.get("app_role") or payload.get("app_metadata", {}).get("app_role")`
- **Severity:** blocker（admin 写操作完全不可用）
- **Status:** **fixed** — BUG-006-FIX 已应用（2026-05-22）；ADMIN-03/05/07 手动复测全 PASS
- **Related:** BUG-005（frontend middleware 同病，已修）；ADMIN-03/05/07 复测 PASS；ADMIN-04 PASS

---

### BUG-007 — Admin 可访问 user-facing /properties 页并触发收藏 403（P2 · Medium/High）

- **ID:** BUG-007
- **Flow:** Admin / Route separation
- **Page/route:** `/properties`
- **User role:** admin
- **Steps to reproduce:** 以 admin 身份登录，访问 `/properties`，点击任意房源收藏按钮
- **Actual result:** admin 可正常访问 `/properties`，页面显示普通用户收藏控件；点击收藏返回 `HTTP 403 Forbidden`（`lib/api/favorites.ts:32`）
- **Expected result:** admin 访问 `/properties` 应被重定向到 `/admin/properties`；或 user-facing 收藏控件不应对 admin 角色显示
- **Root cause:** frontend middleware 只保护 `/admin*` 路由，未限制 admin 进入 user-facing dashboard routes；favorites 后端拒绝 admin 操作是正确行为（admin 不应有收藏记录）；问题在于 admin 不应到达此页面或看到此控件
- **Severity:** medium/high（取决于产品决策：admin 是否允许以普通用户身份浏览；现状是 admin 可浏览但操作残缺）
- **Status:** open — 不修，待授权
- **Related:** ADMIN-04 复测时暴露；BUG-003（middleware 对 auth 用户的 redirect 逻辑）

---

### BUG-008 — Password reset flow missing/broken（P2 · Deferred）

- **ID:** BUG-008
- **Flow:** Password Reset
- **Page/route:** `/login`、`/reset-password`（或等效路由）
- **User role:** any unauthenticated
- **Actual result:**
  1. `/login` 页面无 "Forgot password" / "Reset password" 入口（RESET-01 FAIL）
  2. 无入口导致 reset 表单提交无法测试（RESET-02 BLOCKED）
  3. 即使通过邮件收到 reset 链接，点击后链接打不开（RESET-03 BLOCKED，已知问题）
- **Expected result:** `/login` 有密码重置入口；提交邮箱后显示确认提示；邮件链接可打开 reset 表单并完成密码更新
- **Root cause:** 密码重置 UI 未实现（入口缺失）；reset 链接处理逻辑存在已知问题
- **Severity:** P2 · Deferred（MVP 阶段暂不要求时可推迟；若 MVP 必须则升 P1 · High）
- **Status:** open — 不修，待授权
- **Related:** RESET-01 FAIL；RESET-02/03 BLOCKED

---

## 执行摘要

| 类别 | Total | PASS | FAIL | BLOCKED | SKIPPED |
|------|-------|------|------|---------|---------|
| SEC | 5 | 5 | 0 | 0 | 0 |
| AUTH | 13 | 11 | 2 | 0 | 0 |
| SRCH | 7 | 5 | 1 | 0 | 1 |
| FAV | 7 | 7 | 0 | 0 | 0 |
| ADMIN | 7 | 7 | 0 | 0 | 0 |
| RESET | 3 | 0 | 1 | 2 | 0 |
| **合计** | **42** | **35** | **4** | **2** | **1** |
