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
| SEC-01 | 登录表单提交后 email/password 不出现在 URL | **FAIL** | （原始）URL 出现 `?email=...&password=...` GET 泄露；BUG-001-FIX 后 method=post 改为 POST body，URL 不再泄露，但登录功能中断（BUG-002） | 待 BUG-002 修复后复测 |
| SEC-02 | 登录凭据不出现在 browser history | **FAIL** | 原始 GET URL 进 history；POST 修复后 URL 干净，但功能中断 | 待 BUG-002 修复后复测 |
| SEC-03 | 登录凭据不出现在 Docker logs | **FAIL** | 原始 GET 进 access log；POST 后 log 为 `POST /login 200`，凭据不在路径中 — 部分改善，但功能中断 | 待 BUG-002 修复后复测 |
| SEC-04 | network tab 显示凭据在 POST body，不在 URL params | **FAIL** | POST body 含凭据（form-urlencoded），URL 干净——但为原生 form POST 非 Supabase 调用，功能中断 | 待 BUG-002 修复后复测 |
| SEC-05 | redirectTo 不能跳转到外部域名 | | | 登录功能中断，暂无法测试 |

### Section 1 — Route Protection & redirectTo

| ID | 描述 | Status | Evidence | Notes |
|----|------|--------|----------|-------|
| AUTH-01 | 未登录访问 /properties → /login?redirectTo=/properties | | | |
| AUTH-02 | 未登录访问 /search → /login?redirectTo=/search | | | |
| AUTH-03 | 未登录访问 /favorites → /login?redirectTo=/favorites | | | |
| AUTH-04 | 未登录访问 /admin/properties → 拒绝或重定向 | | | |
| AUTH-05 | 已登录访问 /login → 跳离 auth 页 | | | |
| AUTH-06 | 已登录访问 /register → 跳离 auth 页 | | | |

### Section 2 — Authentication（login/logout/redirectTo 回跳）

| ID | 描述 | Status | Evidence | Notes |
|----|------|--------|----------|-------|
| AUTH-07 | 有效账户登录成功 | | | |
| AUTH-08 | 登录后回跳到 redirectTo 原始路由 | | | |
| AUTH-09 | 无 redirectTo 时落地 /properties | | | |
| AUTH-10 | 登录失败显示错误，表单可继续使用 | | | |
| AUTH-11 | Sign out 清除 session，跳转 /login | | | |
| AUTH-12 | 登出后 browser back 不能回到保护页面 | | | |
| AUTH-13 | 注册：密码不一致显示错误 | | | |

### Section 5 — Search URL State + Clear Filters + Retry

| ID | 描述 | Status | Evidence | Notes |
|----|------|--------|----------|-------|
| SRCH-01 | /search 无筛选加载结果 | | | |
| SRCH-02 | location 搜索更新 URL + 结果 | | | |
| SRCH-03 | 筛选参数持久化到 URL query string | | | |
| SRCH-04 | Clear filters 重置 URL + 结果，不需手动再点 Search | | | |
| SRCH-05 | 搜索分页保留 active filters | | | |
| SRCH-06 | browser back/forward 保持表单状态与结果同步 | | | |
| SRCH-07 | 搜索出错显示 error state，retry 重新执行同一查询（URL 不变时也能重试） | | | |

### Section 6 — Favorites Add/Remove

| ID | 描述 | Status | Evidence | Notes |
|----|------|--------|----------|-------|
| FAV-01 | 列表页可添加收藏 | | | |
| FAV-02 | 列表页可取消收藏 | | | |
| FAV-03 | 详情页可添加收藏 | | | |
| FAV-04 | 详情页可取消收藏 | | | |
| FAV-05 | 重复收藏不破坏 UI（409 静默处理） | | | |
| FAV-06 | /favorites 页列出已收藏房源 | | | |
| FAV-07 | 从 /favorites 页移除收藏后卡片消失 | | | |

### Section 8 — Admin Create/Edit/Delete

| ID | 描述 | Status | Evidence | Notes |
|----|------|--------|----------|-------|
| ADMIN-01 | admin 用户可访问 /admin/properties | | | |
| ADMIN-02 | 非 admin 用户被拦截 | | | |
| ADMIN-03 | 填写表单创建新房源 | | | |
| ADMIN-04 | 新建房源出现在公开列表 | | | |
| ADMIN-05 | 编辑已有房源，保存后变更可见 | | | |
| ADMIN-06 | 取消删除确认不改变数据 | | | |
| ADMIN-07 | 确认删除后房源从列表消失 | | | |

### Section 12 — Password Reset（Known Issue）

| ID | 描述 | Status | Evidence | Notes |
|----|------|--------|----------|-------|
| RESET-01 | /login 页有 "Forgot password" 入口 | | | |
| RESET-02 | 提交 reset 请求后显示确认提示 | | | |
| RESET-03 | 点击邮件中 reset 链接打开 reset 表单 | BLOCKED | 已知问题：reset 链接打不开 | 待修复后验证 |

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

---

## 执行摘要

| 类别 | Total | PASS | FAIL | BLOCKED | SKIPPED |
|------|-------|------|------|---------|---------|
| SEC | 5 | | | | |
| AUTH | 13 | | | | |
| SRCH | 7 | | | | |
| FAV | 7 | | | | |
| ADMIN | 7 | | | | |
| RESET | 3 | | | 1 | |
| **合计** | **42** | | | **1** | |
