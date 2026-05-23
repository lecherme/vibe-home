# Fix Report: BUG-008-FIX

## Ticket Info
- **Review Task:** QA-2026-05-18
- **Affected Task:** PasswordReset — RESET-01 + RESET-02 + RESET-03 — Forgot password flow end-to-end
- **Criterion:** RESET-01
- **Files Declared:** frontend/lib/auth/session.ts, frontend/middleware.ts, frontend/components/features/auth/LoginForm.tsx, frontend/app/(auth)/forgot-password/page.tsx, frontend/components/features/auth/ForgotPasswordForm.tsx, frontend/app/(auth)/reset-password/page.tsx, frontend/components/features/auth/ResetPasswordForm.tsx

## Files Changed
- frontend/lib/auth/session.ts
- frontend/middleware.ts
- frontend/components/features/auth/LoginForm.tsx
- frontend/app/(auth)/forgot-password/page.tsx
- frontend/components/features/auth/ForgotPasswordForm.tsx
- frontend/app/(auth)/reset-password/page.tsx
- frontend/components/features/auth/ResetPasswordForm.tsx

## Patch Summary
Added Supabase password reset and password update session helpers, allowed `/forgot-password` as an auth route, and bypassed redirects for `/reset-password`. Added the forgot-password and reset-password pages/forms, including reset email submission, session validation, password confirmation validation, password update, sign-out, and login redirect.

## Open Issues
Pre-existing unlisted worktree changes are present in `.ai/qa-runs/2026-05-18-post-F9-smoke/fix-tickets.md` and `.ai/qa-runs/2026-05-18-post-F9-smoke/status.json`; I did not modify them.

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec frontend npx tsc --noEmit` | 无输出 | **PASS — exit 0** |
| RESET-01：/login 有 Forgot password 链接，跳 /forgot-password | PASS（2026-05-23） | **PASS** |
| RESET-02：提交 email，触发邮件发送并收到邮件 | PASS（2026-05-23） | **PASS** |
| RESET-03：邮件链接可打开 reset 表单 | Supabase Redirect URL 配置修正后，链接正确落到 /reset-password 表单 | **PASS（2026-05-23）** |
| 密码不一致校验 | 显示校验错误，不提交 | **PASS（2026-05-23）** |
| 无效/过期链接提示 | 显示 "Reset link expired" | **PASS（2026-05-23）** |
| 已登录访问 /forgot-password | 跳转默认页 | **PASS（2026-05-23）** |
| 已登录访问 /reset-password | 正常显示页面，不被踢走 | **PASS（2026-05-23）** |
| 修改成功跳 /login | 正确跳转 | **PASS（2026-05-23）** |
| 新密码登录 | 新密码登录成功 | **PASS（2026-05-23）** |

## Notes
- RESET-03 链接是 localhost 的根因：**Supabase Auth 控制台的 Site URL / Redirect URLs 配置仍为 localhost**，Supabase 以自身配置覆盖 `redirectTo` 参数中的域名。前端代码（`window.location.origin`）无问题。已调整 Supabase 配置，需重新发送 reset 邮件复测。
- BUG-008-FIX 状态保持 partial，等完整复测后更新。
