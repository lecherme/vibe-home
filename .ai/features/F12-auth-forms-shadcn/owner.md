# F12 Auth Forms shadcn/ui Migration — Ownership Boundaries

This is a static ownership map. Runtime state comes from `status.json`.

---

## T01（Codex）— 创建 auth Zod schemas

**允许修改的文件：**
- `frontend/lib/schemas/auth.ts`（新建）

**不得修改：** `frontend/app/`、`frontend/components/`、`frontend/lib/auth/`、`frontend/types/`、`backend/`、`status.json`

---

## T02（Gemini）— 迁移 4 个 auth 表单

**允许修改的文件：**
- `frontend/components/features/auth/LoginForm.tsx`
- `frontend/components/features/auth/RegisterForm.tsx`
- `frontend/components/features/auth/ForgotPasswordForm.tsx`
- `frontend/components/features/auth/ResetPasswordForm.tsx`

**不得修改：** `frontend/app/`、`frontend/lib/`（只读）、`frontend/types/`（只读）、`backend/`、`status.json`

**强制约束（SEC-01）：** `LoginForm.tsx` 的 `<form>` 标签必须保留 `method="post"`，不得删除。

---

## T03（Codex）— Review

只读审查，不得修改任何源文件。输出 review report 到 stdout，由 harness 写入 `review.md`。

---

## T04（Claude）— Acceptance

Claude 写 `final-report.md` 并更新 `status.json`。

**允许修改的文件：**
- `.ai/features/F12-auth-forms-shadcn/status.json`
- `.ai/features/F12-auth-forms-shadcn/final-report.md`

---

## Boundary Rules（全阶段适用）

1. Workers 不得修改 `status.json`。
2. Workers 不得直接创建报告文件；harness 脚本负责将 stdout 写入 artifact。
3. Workers 不得修改当前任务 scope 之外的文件。
4. `frontend/app/` 页面文件在本 feature 中不得修改。
5. 不修改 `backend/` 任何文件。
6. `frontend/lib/auth/password-validation.ts` 只引用，不修改。
7. **SEC-01 强制**：`LoginForm.tsx` 中 `<form>` 必须保留 `method="post"`，防止凭据出现在 URL 中。
8. **非表单 state 保留**：`RegisterForm` 和 `ForgotPasswordForm` 的 `isSuccess`、`ResetPasswordForm` 的 `isCheckingSession`/`hasValidSession` 必须保留为 `useState`，不得迁移至 react-hook-form。
9. **Button 样式显式写**：`globals.css` 无 shadcn CSS 变量，所有 Button 颜色必须用显式 Tailwind class（`bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50`）。
