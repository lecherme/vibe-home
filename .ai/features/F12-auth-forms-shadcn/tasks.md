# F12 Auth Forms shadcn/ui Migration — Tasks

---

## T01 — Codex: 创建 auth Zod schemas

- **owner:** codex
- **type:** build
- **depends_on:** none
- **allowed files:**
  - `frontend/lib/schemas/auth.ts`

**Requirements:**

新建 `frontend/lib/schemas/auth.ts`，导出以下 4 个 schema 和对应类型：

```ts
import { z } from "zod"
import { validatePassword } from "@/lib/auth/password-validation"

export const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
})
export type LoginFormValues = z.infer<typeof loginSchema>

export const registerSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().superRefine((val, ctx) => {
    const error = validatePassword(val)
    if (error) ctx.addIssue({ code: z.ZodIssueCode.custom, message: error })
  }),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"],
})
export type RegisterFormValues = z.infer<typeof registerSchema>

export const forgotPasswordSchema = z.object({
  email: z.string().email("Invalid email address"),
})
export type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>

export const resetPasswordSchema = z.object({
  password: z.string().superRefine((val, ctx) => {
    const error = validatePassword(val)
    if (error) ctx.addIssue({ code: z.ZodIssueCode.custom, message: error })
  }),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"],
})
export type ResetPasswordFormValues = z.infer<typeof resetPasswordSchema>
```

验证：`docker compose exec frontend npx tsc --noEmit` exit 0。不修改任何其他文件。

---

## T02 — Gemini: 迁移 4 个 auth 表单

- **owner:** gemini
- **type:** build
- **depends_on:** T01
- **allowed files:**
  - `frontend/components/features/auth/LoginForm.tsx`
  - `frontend/components/features/auth/RegisterForm.tsx`
  - `frontend/components/features/auth/ForgotPasswordForm.tsx`
  - `frontend/components/features/auth/ResetPasswordForm.tsx`

**Requirements:**

对所有 4 个表单的共同要求：
- 导入 `useForm` from `react-hook-form`，`zodResolver` from `@hookform/resolvers/zod`
- 导入对应 schema 和类型 from `@/lib/schemas/auth`
- 导入 shadcn Form 组件：`Form`、`FormField`、`FormItem`、`FormLabel`、`FormControl`、`FormMessage` from `@/components/ui/form`
- 导入 shadcn `Input` from `@/components/ui/input`，`Button` from `@/components/ui/button`
- 移除手写 `useState` 字段状态（email、password、confirmPassword 等），改为 `useForm` 管理
- 按钮颜色显式写，不依赖 shadcn CSS 变量：`className="... bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 ..."`

### LoginForm.tsx

1. 使用 `loginSchema` / `LoginFormValues`
2. `<form>` 标签保留 `method="post"`（**SEC-01 强制要求，不得删除**）
3. 保留 `useRouter`、`useSearchParams`、`sanitizedRedirectTo`、`getRoleFromSession`、`getSession`、`signIn` 逻辑
4. 服务端错误（signIn 抛出）通过独立 `useState<string | null>` 展示，不纳入 Zod schema
5. 提交按钮用 shadcn `Button`，disabled 条件：`form.formState.isSubmitting`

### RegisterForm.tsx

1. 使用 `registerSchema` / `RegisterFormValues`
2. 移除手写密码校验（`validatePassword` 调用、`password !== confirmPassword` 检查），已在 schema 中处理
3. **保留 `isSuccess` state** 和成功后展示界面（绿色提示 + 3 秒后跳转 /login 的 `useEffect`）
4. 服务端错误通过独立 `useState<string | null>` 展示

### ForgotPasswordForm.tsx

1. 使用 `forgotPasswordSchema` / `ForgotPasswordFormValues`
2. **保留 `isSuccess` state** 和成功后展示界面
3. 服务端错误通过独立 `useState<string | null>` 展示

### ResetPasswordForm.tsx

1. 使用 `resetPasswordSchema` / `ResetPasswordFormValues`
2. 移除手写密码校验，已在 schema 中处理
3. **保留全部 3 个 `useState`**：`isCheckingSession`、`hasValidSession`、`isLoading`（submit 期间）
4. **保留 `useEffect` session 检查逻辑**（mount 时调用 `getSession`，设置 hasValidSession）
5. **保留 3 个条件渲染分支**：checking / expired / form
6. 服务端错误通过独立 `useState<string | null>` 展示

验证：`docker compose exec frontend npx tsc --noEmit` exit 0。不修改任何其他文件。

---

## T03 — Codex: review

- **owner:** codex
- **type:** review
- **depends_on:** T01, T02

Review against acceptance.md criteria.

---

## T04 — Claude: acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T03
