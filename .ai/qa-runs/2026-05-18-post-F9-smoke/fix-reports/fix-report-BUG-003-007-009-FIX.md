# Fix Report: BUG-003-007-009-FIX

## Ticket Info
- **Review Task:** QA-2026-05-18
- **Affected Task:** RoleLanding — BUG-003 + BUG-007 + BUG-009 — role landing / route separation / NavBar navigation
- **Criterion:** BUG-003
- **Files Declared:** frontend/lib/auth/roles.ts, frontend/middleware.ts, frontend/components/features/auth/LoginForm.tsx, frontend/app/(dashboard)/layout.tsx, frontend/components/features/properties/NavBar.tsx

## Files Changed
- frontend/lib/auth/roles.ts
- frontend/middleware.ts
- frontend/components/features/auth/LoginForm.tsx
- frontend/app/(dashboard)/layout.tsx
- frontend/components/features/properties/NavBar.tsx

## Patch Summary
Added shared role utilities for JWT/session role extraction, default role landing pages, and redirect sanitization. Replaced inline middleware role logic with role-based auth/admin/user-route redirects, updated login to read the post-login session before landing by role, and passed the server-derived role into NavBar for role-specific navigation.

## Open Issues
None.

## Claude Fallback Correction

**Authorization:** 用户授权 — "授权 Claude fallback 修正这两个 worker patch 逻辑问题"

Codex worker 产出 patch 后，发现两处逻辑错误由 Claude 修正：

1. **`frontend/lib/auth/roles.ts` — `sanitizeRedirectTo` 未排除 `"/"`**
   - Worker 实现：`"/"` 通过 `startsWith("/")` 检查，被视为合法 redirectTo 返回，BUG-003 根因未消除
   - Claude 修正：加 `raw === "/"` 判断，对 null / `"/"` / 非相对路径 / `"//"` 一律返回 `null`（而非 `"/properties"`）

2. **`frontend/components/features/auth/LoginForm.tsx:28` — router.push 永远忽略 redirectTo**
   - Worker 实现：`router.push(redirectTo === defaultPage ? redirectTo : defaultPage)` 两分支等价，有效 redirectTo（如 `/search`）被忽略
   - Claude 修正：重命名为 `sanitizedRedirectTo`，登录后改为 `router.push(sanitizedRedirectTo ?? getDefaultPage(role))`，保留有效 redirectTo

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec frontend npx tsc --noEmit` (wrapper 命令格式错误) | `error TS5025` | FAIL（wrapper bug，非代码错误）|
| `docker compose exec frontend npx tsc --noEmit`（Claude fallback 后重跑） | 无输出 | **PASS — exit 0** |
