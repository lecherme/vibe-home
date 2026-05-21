# QA Fix Tickets — 2026-05-18-post-F9-smoke

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
- **Status:** pending

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
- **Status:** pending

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
- **Status:** pending → fixed pending verification（待 Claude diff/scope/tsc 验证后更新）
