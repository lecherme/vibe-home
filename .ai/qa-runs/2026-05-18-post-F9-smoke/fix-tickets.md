# QA Fix Tickets — 2026-05-18-post-F9-smoke

## BUG-004-FIX

- **Bug:** BUG-004 — Clear Filters 仅在 no-results 状态显示
- **Owner:** Codex + Claude fallback（布局调整）
- **Severity:** P2 / Medium
- **Allowed files:**
  - `frontend/app/(dashboard)/search/page.tsx`
  - `frontend/components/features/search/search-bar.tsx` ← Claude fallback 授权扩大 scope
- **Requirements:**
  1. 在 `SearchContent` 中计算 `hasActiveFilters`：`location` 非空，或 `filters.min_price / max_price / bedrooms / status` 任一有值，则为 true（已存在，不变）
  2. 将 Clear Filters 按钮放在 `<SearchBar>` 同一行右侧（与 Search 按钮并排）：用 `flex flex-wrap items-center gap-2` 包裹，`<SearchBar>` 占 `flex-1 min-w-0`，Clear Filters 按钮紧跟其后
  3. Clear Filters 按钮始终渲染；`hasActiveFilters === true` 时 enabled，否则 `disabled`；点击调用已有的 `handleClearFilters()`；padding/font/radius 与 Search 按钮一致
  4. 移除 FilterPanel 下方/结果区上方的旧 Clear Filters 区块
  5. 保留 no-results 状态下已有的 "Clear all filters" 按钮，不改动
  6. input 加 `py-2 text-sm` 使高度与按钮一致
  7. Search 按钮加 `w-28 shrink-0 justify-center`，loading 态文字变化不引起宽度抖动
  8. 不新增函数，不改动 `handleClearFilters` 逻辑
  9. tsc 通过
- **Verification:** `docker compose exec frontend npx tsc --noEmit` exit 0；手动复测 SRCH-04
- **Claude Fallback Authorization:**
  - 第一次：用户授权扩大 scope 到 `search-bar.tsx`，调整 input/Search 高度与按钮视觉一致性（2026-05-22）
  - 第二次：用户授权修复 Search 按钮 loading 态宽度抖动，加 `w-28 shrink-0 justify-center`（2026-05-22）
- **Status:** verified — tsc exit 0；SRCH-04 手动复测 PASS（2026-05-22）

---

## BUG-003-007-009-FIX

- **Bugs:** BUG-003 (redirectTo=/ → HealthPage) + BUG-007 (admin 访问 user-facing routes) + BUG-009 (NavBar 无导航/角色感知)
- **Owner:** Codex
- **Severity:** P1 / High
- **Allowed files:**
  1. `frontend/lib/auth/roles.ts` ← 新建
  2. `frontend/middleware.ts`
  3. `frontend/components/features/auth/LoginForm.tsx`
  4. `frontend/app/(dashboard)/layout.tsx`
  5. `frontend/components/features/properties/NavBar.tsx`
- **Requirements:**

  **A. 新建 `frontend/lib/auth/roles.ts`（纯 utility，无副作用）**
  ```ts
  import type { Session } from "@supabase/supabase-js";

  export type AppRole = "user" | "admin";

  // 兼容 JWT 顶层 app_role 和 app_metadata.app_role
  export function getRoleFromJwt(token: string): AppRole {
    // base64url decode JWT payload，读取 app_role 或 app_metadata.app_role
    // 返回 "admin" 或 "user"
  }

  export function getRoleFromSession(session: Session | null): AppRole {
    if (!session) return "user";
    return getRoleFromJwt(session.access_token);
  }

  export function getDefaultPage(role: AppRole): string {
    return role === "admin" ? "/admin/properties" : "/properties";
  }

  // 返回合法的 redirectTo（相对路径、非 "/"）；否则返回 null
  export function sanitizeRedirectTo(raw: string | null): string | null {
    if (!raw) return null;
    if (!raw.startsWith("/") || raw.startsWith("//") || raw === "/") return null;
    return raw;
  }
  ```

  **B. `frontend/middleware.ts`**
  - 移除内联 `JwtPayload` interface 和 `decodeJwtPayload`，改用 `getRoleFromSession` from roles.ts
  - 块 1（已有）：未登录 + 非 auth route → `/login?redirectTo=...`（不变）
  - 块 2（修改）：已登录 + auth route (`/login`, `/register`) → `getDefaultPage(role)` 按角色跳转（不再硬跳 `/`）
  - 块 3（新增）：已登录 + admin + user-facing route（`/`、`/properties*`、`/search*`、`/favorites*`）→ `/admin/properties`
  - 块 4（修改）：已登录 + 非 admin + admin route → `/properties`（不再跳 `/`）

  **C. `frontend/components/features/auth/LoginForm.tsx`**
  - 移除内联 redirectTo 校验逻辑，改用 `sanitizeRedirectTo` from roles.ts
  - 登录后默认页：移除硬编码 `"/properties"`，改为调 `supabase.auth.getSession()` 后用 `getDefaultPage(role)` 确定落点
  - `redirectTo=null` 时（sanitize 过滤掉 `/`）→ push 到 `getDefaultPage(role)`

  **D. `frontend/app/(dashboard)/layout.tsx`**
  - 改为 async server component
  - 用 `createServerClient` from `@supabase/ssr` + `cookies()` from `next/headers` 创建服务端 Supabase client
  - 调 `supabase.auth.getSession()` 获取 session
  - 用 `getRoleFromSession(session)` 从 roles.ts 获取 role
  - 将 `role` 作为 prop 传给 `<NavBar role={role} />`

  **E. `frontend/components/features/properties/NavBar.tsx`**
  - 接收 `role: AppRole` prop（从 layout server-side 传入，无 useEffect）
  - user role → 渲染导航链接：Properties (`/properties`) / Search (`/search`) / Favorites (`/favorites`) / Sign out
  - admin role → 渲染导航链接：Admin Console (`/admin/properties`) / Sign out
  - 移除对 role 无感知的静态渲染

- **Verification:** `npx tsc --noEmit` exit 0（在 frontend container 内）
- **Acceptance criteria（手动复测）:**
  1. 普通用户无 redirectTo 登录 → `/properties`
  2. admin 无 redirectTo 登录 → `/admin/properties`
  3. `redirectTo=/` 登录 → 按角色默认页
  4. 已登录访问 `/login` / `/register` → 按角色默认页
  5. admin 访问 `/properties` / `/search` / `/favorites` → `/admin/properties`
  6. 普通用户访问 `/admin/properties` → `/properties`
  7. NavBar 普通用户：显示 Properties / Search / Favorites / Sign out
  8. NavBar admin：显示 Admin Console / Sign out
- **Status:** verified — tsc exit 0；AC-01/02/03/04a/05/06/07/08 手动复测 PASS（2026-05-22）；Claude fallback 修正 sanitizeRedirectTo 和 LoginForm router.push 逻辑

---

## BUG-006-FIX

- **Bug:** BUG-006 — 后端 admin role claim mismatch（security.py 读取顶层 app_role，Supabase 实际存在 app_metadata.app_role）
- **Owner:** Codex
- **Severity:** P0 / Blocker
- **Attempt:** FIX-1
- **Allowed files:**
  - `backend/app/core/security.py`
- **Requirements:**
  1. `get_current_user` 中 L71 `raw_role = payload.get("app_role")` 改为：先读顶层 `app_role`，fallback 读 `app_metadata.app_role`：`raw_role = payload.get("app_role") or payload.get("app_metadata", {}).get("app_role")`
  2. 不修改其他任何文件
  3. 容器内跑 `pytest` 或相关后端验证通过
- **Verification:** `docker compose exec backend pytest` 或等效检查 exit 0
- **Status:** verified — `py_compile` pass；ADMIN-03/05/07 手动复测全 PASS（2026-05-22）

---

## BUG-005-FIX

- **Bug:** BUG-005 — Admin role claim mismatch（middleware 读取顶层 app_role，Supabase 实际存在 app_metadata.app_role）
- **Owner:** Codex
- **Severity:** P0 / Blocker
- **Attempt:** FIX-1
- **Allowed files:**
  - `frontend/middleware.ts`
- **Requirements:**
  1. `JwtPayload` interface 增加 `app_metadata?: { app_role?: AppRole }` 字段
  2. admin role 读取逻辑改为：先读顶层 `payload.app_role`，fallback 读 `payload.app_metadata?.app_role`（兼容两种 claim 结构）
  3. 不修改其他任何文件
  4. tsc 通过（`npx tsc --noEmit`）
- **Verification:** tsc exit 0；手动复测 ADMIN-01
- **Status:** verified — tsc exit 0；ADMIN-01 手动复测 PASS（2026-05-21）

---

## BUG-002-FIX-1

- **Bug:** BUG-002 — 登录无反应（React onSubmit 未拦截，hydration 待确认）
- **Owner:** Gemini
- **Severity:** P0 / Blocker
- **Attempt:** FIX-1（allowedDevOrigins — HMR/dev resource blocked hypothesis）
- **Allowed files:**
  - `frontend/next.config.mjs`
- **Requirements:**
  1. `next.config.mjs` 添加 `allowedDevOrigins: ["192.168.31.136", "192.168.31.221", "100.102.19.18"]`
  2. 不修改其他任何文件
  3. 重启 frontend container 后复测：Console 无 blocked cross-origin 警告；Network tab 显示 Supabase auth 请求而非 POST /login；登录成功跳转
- **Verification:** 重启后手动复测 — Console 干净 + 登录功能恢复
- **Note:** BUG-002 不标 fixed；本 ticket 为 fix attempt，结果 pending verification
- **Status:** verified — 三项环境配置修复后登录恢复；BUG-002 closed（2026-05-18）

---

## BUG-001-FIX

- **Bug:** BUG-001 — LoginForm GET 凭据泄露
- **Owner:** Gemini
- **Severity:** P0 / Blocker
- **Allowed files:**
  - `frontend/components/features/auth/LoginForm.tsx`
  - `frontend/app/(auth)/login/page.tsx`
- **Requirements:**
  1. `LoginForm.tsx` 的 `<form>` 标签加 `method="post"`
  2. `login/page.tsx` 用 `<Suspense>` 包裹 `<LoginForm />`（`LoginForm` 内有 `useSearchParams()`，需要 Suspense boundary）
  3. 不修改其他任何文件
  4. tsc 通过
- **Verification:** tsc exit 0
- **Status:** verified — tsc exit 0；SEC-01~04 手动复测全 PASS（2026-05-18）
