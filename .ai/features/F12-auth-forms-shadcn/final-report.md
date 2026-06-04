# F12 Auth Forms shadcn/ui Migration — Claude Acceptance Report (T04)

**Date:** 2026-06-04
**Reviewer:** Claude (T04 acceptance owner)

## Disposition: ACCEPTED

---

## Feature Summary

F12 将 4 个 auth 表单迁移至 shadcn/ui + react-hook-form + Zod，复用 F11 建立的模式：

- **T01 (Codex):** 新建 `frontend/lib/schemas/auth.ts`，4 个 schema 均符合规格。
- **T02 (Gemini):** 迁移 4 个 auth 表单，保留全部关键约束（SEC-01 `method="post"`、isSuccess/isCheckingSession/hasValidSession state、显式 Button 颜色）。
- **T03 (Codex review):** 首轮 PASS，14 条全通过，无 Required Fixes。
- **T04 (Claude):** 本报告。

**验收过程中发现并修复的 pre-existing bug（BUG-008 遗留）：**
Supabase PKCE password reset flow 在邮件客户端 WebView 打开时 verifier 不可用。修复方案：新增 `/auth/callback` route + middleware 放行 + `session.ts` 加 `verifyPasswordRecovery`（`verifyOtp` + `token_hash`）+ `ResetPasswordForm` 改为 `token_hash` 流程 + Supabase 邮件模板更新。

---

## Criteria Results

| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 — loginSchema 正确 | PASS | |
| A2 — registerSchema 正确 | PASS | |
| A3 — forgotPasswordSchema 正确 | PASS | |
| A4 — resetPasswordSchema 正确 | PASS | |
| A5 — LoginForm 迁移 | PASS | `method="post"` 保留 |
| A6 — RegisterForm 迁移 | PASS | isSuccess 保留，3 秒跳转 /login |
| A7 — ForgotPasswordForm 迁移 | PASS | isSuccess 保留 |
| A8 — ResetPasswordForm 迁移 | PASS | isCheckingSession + hasValidSession + 3 分支保留 |
| A9 — tsc 通过 | PASS | exit 0 |
| A10 — 登录 happy path | PASS | 用户手测通过 |
| A11 — 注册 happy path | PASS | 用户手测通过 |
| A12 — forgot password happy path | PASS | 用户手测通过 |
| A13 — reset password happy path | PASS | 用户手测通过（token_hash 流程） |
| A14 — 其他文件未改动 | PASS | hotfix 文件在 F12 scope 外单独记录 |

---

## Accepted
