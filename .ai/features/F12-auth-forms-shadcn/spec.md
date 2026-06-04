# F12 — Auth Forms shadcn/ui Migration

**Status:** in_progress  
**Created:** 2026-06-04

## Goal

将 4 个 auth 表单迁移至 shadcn/ui + react-hook-form + Zod，复用 F11 建立的模式。目标是统一 auth 表单的校验、错误展示、提交状态，并通过 Zod schema 规范化 cross-field 校验（确认密码、密码规则）。

## Scope

### In scope
- 新建 `frontend/lib/schemas/auth.ts`：loginSchema、registerSchema、forgotPasswordSchema、resetPasswordSchema
- 迁移 4 个组件：LoginForm、RegisterForm、ForgotPasswordForm、ResetPasswordForm
- `validatePassword` 通过 Zod `.superRefine()` 集成进 password 字段 schema

### Out of scope
- 修改 `lib/auth/password-validation.ts`（只引用，不改）
- 修改 `lib/auth/session.ts` 或其他 auth lib
- 修改任何 app 页面
- 安装新依赖（F11 已装好）
- filter-panel、search-bar、PaginationControls 等（留 F13）

## Critical Constraints

1. **LoginForm 必须保留 `method="post"`** — BUG-001 / SEC-01 要求，防止凭据出现在 URL
2. **非表单 state 保留为 useState**：
   - RegisterForm: `isSuccess`（注册成功后展示成功界面）
   - ForgotPasswordForm: `isSuccess`
   - ResetPasswordForm: `isCheckingSession`、`hasValidSession`（session 检查 + 过期界面）
3. **Button 样式显式写**：用 `className="... bg-indigo-600 text-white hover:bg-indigo-700 ..."` 而非依赖 shadcn CSS 变量（globals.css 无 CSS vars）
4. 不修改 `backend/` 任何文件
