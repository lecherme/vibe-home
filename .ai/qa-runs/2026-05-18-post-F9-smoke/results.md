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
| AUTH-05 | 已登录访问 /login → 跳离 auth 页 | **PASS** | BUG-003-007-009-FIX 后，普通用户已登录访问 `/login` → 正确跳转 `/properties` | BUG-003-FIX 有效 |
| AUTH-06 | 已登录访问 /register → 跳离 auth 页 | **PASS** | BUG-003-007-009-FIX 后，按角色默认页跳转（普通用户 → `/properties`，admin → `/admin/properties`） | BUG-003-FIX 有效 |

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
- **Status:** **fixed** — BUG-003-007-009-FIX 已应用（2026-05-22）；AC-01/03/04a 手动复测 PASS；AUTH-05/06 更新为 PASS
- **附加影响:** 根路由 `/`（HealthPage）无 Sign Out 按钮和导航入口，用户落到此页后需手动导航到 `/properties` 才能登出；BUG-003 修复后复评

---

### BUG-004 — /search Clear Filters 仅在 No Results 状态显示（P2 · Medium）

- **ID:** BUG-004
- **Flow:** Search
- **Page/route:** `/search`
- **User role:** any authenticated
- **Steps to reproduce:** 设置筛选条件，在有结果的状态下寻找清除/重置按钮
- **Actual result:** "Clear all filters" 按钮只在「无结果」状态下渲染（`search/page.tsx`）；有筛选条件且有结果时，用户无法清除 filters，必须手动逐个重置
- **Expected result:** Clear Filters 按钮应始终可见（或在有 active filters 时显示），无论是否有搜索结果
- **Root cause（已确认）:** `frontend/app/(dashboard)/search/page.tsx` 中 Clear Filters 按钮在 no-results 条件块内渲染，active filters + 有结果时不渲染
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
- **Status:** **fixed** — BUG-003-007-009-FIX 已应用（2026-05-22）；AC-05 手动复测 PASS（admin 访问 /properties → /admin/properties）
- **Related:** ADMIN-04 复测时暴露；BUG-003（已修）；BUG-009（已修）

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

### BUG-009 — NavBar 缺少主导航链接 / 无角色感知（P1 · High）

- **ID:** BUG-009
- **Flow:** Navigation
- **Page/route:** NavBar（所有 dashboard 页面）
- **User role:** any authenticated
- **Actual result:** NavBar 无 /search、/favorites 链接；admin 无 /admin/properties 链接；所有角色均无法通过 NavBar 导航，只能手动输入 URL
- **Expected result:** NavBar 应包含角色感知链接 — 普通用户显示 /properties、/search、/favorites；admin 显示 /admin/properties（或至少有入口）
- **Root cause:** `frontend/components/features/properties/NavBar.tsx` 为静态组件，未读取用户 role，未渲染 /search、/favorites、/admin 链接
- **Severity:** high（app 实际不可导航，所有路由靠手动 URL 访问）
- **Status:** **fixed** — BUG-003-007-009-FIX 已应用（2026-05-22）；AC-07/08 手动复测 PASS（NavBar 按角色正确渲染）
- **Related:** BUG-003（已修）；BUG-007（已修）；Gemini audit NEW-001/002

---

### BUG-010 — Favorites 分页缺失 + favorite-state 上限不一致（P2 · Medium）

- **ID:** BUG-010
- **Flow:** Favorites
- **Page/route:** `/favorites`、`/search`
- **User role:** any authenticated
- **Actual result:**
  1. `/favorites` 页 pageSize=12，无分页 UI；>12 条收藏永远看不到（`favorites/page.tsx`）
  2. `/search` 页 getFavorites 请求 page_size=100，但 backend favorites 接口上限为 50；>50 条收藏时搜索结果中收藏状态显示为未收藏（"ghost unfavorited"）
- **Expected result:** /favorites 页应支持分页；frontend 请求 page_size 应与 backend 上限对齐，或 backend 提供全量收藏接口
- **Root cause:** `favorites/page.tsx` 无分页组件；`search/page.tsx` hardcode page_size=100；`backend/app/api/v1/favorites/router.py` max page_size=50
- **Severity:** medium
- **Status:** open — 不修，待授权
- **Related:** Gemini audit NEW-005/008

---

### BUG-011 — Admin 房源列表无分页（P2 · Medium）

- **ID:** BUG-011
- **Flow:** Admin
- **Page/route:** `/admin/properties`
- **User role:** admin
- **Actual result:** `admin/properties/page.tsx` 固定请求 page_size=100，无分页 UI；房源超过 100 条时无法访问后续数据，且单次加载性能随数据量线性下降
- **Expected result:** admin 列表应支持分页或无限滚动
- **Root cause:** `frontend/app/(dashboard)/admin/properties/page.tsx` hardcode page_size=100，无分页组件
- **Severity:** medium（当前数据量小影响有限；规模增长后为 high）
- **Status:** open — 不修，待授权
- **Related:** Gemini audit NEW-003

---

### BUG-012 — Admin 表单 image_url（string）与 Property 类型 images（array）不一致（P3 · Low）

- **ID:** BUG-012
- **Flow:** Admin / Data model
- **Page/route:** `/admin/properties`
- **User role:** admin
- **Actual result:** `property-form.tsx` 使用 `image_url`（单字符串）提交；核心 `Property` 类型期望 `images`（数组）；admin 每次只能上传一张图，且存在字段映射开销
- **Expected result:** 表单支持多图 URL 或与 Property 数据模型对齐
- **Root cause:** `frontend/components/features/admin/property-form.tsx` 数据模型未与 `Property` 类型同步
- **Severity:** low（功能可用，限制为单图）
- **Status:** open — 不修，待授权
- **Related:** Gemini audit NEW-009

---

### BUG-013 — 生产环境 API URL 无 fallback，部署风险（P2 · Medium）

- **ID:** BUG-013
- **Flow:** Configuration / Deployment
- **Page/route:** N/A
- **User role:** N/A
- **Actual result:** `frontend/lib/api/properties.ts` 中 `NEXT_PUBLIC_API_URL` 缺省 fallback 为 `localhost:8000`；生产环境漏配环境变量时，浏览器请求会打到用户本机，导致全站 API 不可用且报错不明显
- **Expected result:** 缺少环境变量时应 build 报错或有明确 fallback，不应静默 fallback 到 localhost
- **Severity:** medium（开发环境无影响；生产部署失误时影响全部 API）
- **Status:** open — 不修，待授权
- **Related:** BUG-002（开发环境同类配置问题）；Gemini audit NEW-004

---

### BUG-014 — 注册成功后未引导用户登录（P3 · Low）

- **ID:** BUG-014
- **Flow:** Authentication / Onboarding
- **Page/route:** `/register`
- **User role:** unauthenticated
- **Actual result:** `RegisterForm.tsx` 注册成功后显示 success message，停留在 /register；用户需手动导航到 /login，增加摩擦
- **Expected result:** 注册成功后自动跳转到 /login（或直接登录跳转到 /properties）
- **Severity:** low
- **Status:** open — 不修，待授权
- **Related:** Gemini audit NEW-010

---

## Observations / Backlog（不开 bug，待产品决策）

| ID | 来源 | 描述 |
|----|------|------|
| OBS-001 | SRCH-03 / Gemini NEW-006 | 搜索 UX 不一致：price/beds 字段实时触发搜索，location 需手动 Enter/Submit；混合体验待产品决策 |
| OBS-002 | Gemini NEW-007 | getFavorites 请求失败时静默降级，搜索页所有房源显示为未收藏而非报错；可接受还是需要 error state 待产品决策 |
| OBS-003 | FAV 测试 / Gemini NEW-012 | 收藏操作为乐观更新，API 失败时图标静默回滚，无 toast/error 提示；是否需要失败反馈待产品决策 |
| OBS-004 | Gemini NEW-013 | AuthRateLimiter 为 in-memory + path-specific，不支持多实例横向扩展；单实例部署下无影响，扩容前需替换为 Redis 等分布式方案 |
| OBS-005 | Gemini NEW-014 | 登录/注册表单无「显示密码」toggle，密码输入易误；UX polish，低优先级 |
| OBS-006 | AC-07 复测 | 房源图片加载失败：`picsum.photos` ERR_NAME_NOT_RESOLVED（dev 网络 DNS 无法解析外部域名），Supabase Storage URL 来自不同项目（`ethrhylyxtoirnemsady` vs 配置的 `qldkxgeevgoojtthfvhx`），疑似数据库中存有旧项目的 stale image URL；不影响功能逻辑 |

---

## 执行摘要

| 类别 | Total | PASS | FAIL | BLOCKED | SKIPPED |
|------|-------|------|------|---------|---------|
| SEC | 5 | 5 | 0 | 0 | 0 |
| AUTH | 13 | 13 | 0 | 0 | 0 |
| SRCH | 7 | 5 | 1 | 0 | 1 |
| FAV | 7 | 7 | 0 | 0 | 0 |
| ADMIN | 7 | 7 | 0 | 0 | 0 |
| RESET | 3 | 0 | 1 | 2 | 0 |
| **合计** | **42** | **37** | **2** | **2** | **1** |
