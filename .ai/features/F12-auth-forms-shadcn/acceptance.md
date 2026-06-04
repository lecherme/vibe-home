# F12 Auth Forms shadcn/ui Migration — Acceptance Criteria

## A1 — loginSchema 正确
`frontend/lib/schemas/auth.ts` 中 `loginSchema` 覆盖 email（有效 email 格式）和 password（非空）。

## A2 — registerSchema 正确
`registerSchema` 覆盖 email、password（`.superRefine` 集成 `validatePassword`）、confirmPassword，并有 `.refine` 确保两次密码一致，错误挂在 `confirmPassword` 路径。

## A3 — forgotPasswordSchema 正确
`forgotPasswordSchema` 覆盖 email（有效 email 格式）。

## A4 — resetPasswordSchema 正确
`resetPasswordSchema` 覆盖 password（`.superRefine` 集成 `validatePassword`）和 confirmPassword，并有 `.refine` 确保两次密码一致。

## A5 — LoginForm 迁移
LoginForm 使用 shadcn Form + react-hook-form + loginSchema，`<form>` 保留 `method="post"`（SEC-01）。

## A6 — RegisterForm 迁移
RegisterForm 使用 shadcn Form + react-hook-form + registerSchema，`isSuccess` state 保留，成功后展示成功界面并在 3 秒后跳转 /login。

## A7 — ForgotPasswordForm 迁移
ForgotPasswordForm 使用 shadcn Form + react-hook-form + forgotPasswordSchema，`isSuccess` state 保留，成功后展示成功界面。

## A8 — ResetPasswordForm 迁移
ResetPasswordForm 使用 shadcn Form + react-hook-form + resetPasswordSchema，`isCheckingSession` 和 `hasValidSession` state 保留，三个条件渲染分支（checking / expired / form）均保留。

## A9 — tsc 通过
`docker compose exec frontend npx tsc --noEmit` exit 0。

## A10 — 登录 happy path 通过
用有效账号登录 → 跳转到对应 dashboard。

## A11 — 注册 happy path 通过
用新邮箱注册 → 展示成功提示 → 3 秒后跳转 /login。

## A12 — forgot password happy path 通过
提交 email → 展示"check your email"成功提示。

## A13 — reset password happy path 通过
通过 reset link 进入页面 → 填写新密码 → 提交 → 跳转 /login。

## A14 — 其他文件未改动
`frontend/app/`、`frontend/lib/`（除新建 `schemas/auth.ts`）、`backend/`、其他 components 无修改。
