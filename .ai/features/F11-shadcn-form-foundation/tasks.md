# F11 shadcn/ui Form Foundation — Tasks

---

## T01 — Codex: 安装依赖和 shadcn 组件

- **owner:** codex
- **type:** build
- **depends_on:** none
- **allowed files:**
  - `frontend/package.json`
  - `frontend/package-lock.json`
  - `frontend/components/ui/*`
  - `frontend/hooks/*`

**Requirements:**

1. 在 `frontend/package.json` 添加以下依赖（版本兼容 React 18 / Next 16）：
   - `zod`
   - `react-hook-form`
   - `@hookform/resolvers`
   - `lucide-react`
   - 所需 `@radix-ui/*` 包（由 shadcn 组件引入）
2. 运行 `npx shadcn@latest add button input textarea select dialog table toast form label` 生成对应组件文件到 `frontend/components/ui/`
3. 验证：`docker compose exec frontend npx tsc --noEmit` exit 0
4. 不修改任何 `frontend/app/`、`frontend/components/features/`、`frontend/lib/` 文件

---

## T02 — Gemini: 迁移 property-form.tsx

- **owner:** gemini
- **type:** build
- **depends_on:** T01
- **allowed files:**
  - `frontend/components/features/admin/property-form.tsx`
  - `frontend/lib/schemas/property.ts`

**Requirements:**

### Zod Schema（新文件 `frontend/lib/schemas/property.ts`）

1. 定义并导出 `propertySchema`：
   ```ts
   import { z } from "zod"
   export const propertySchema = z.object({
     title: z.string().min(1, "Title is required"),
     description: z.string().min(1, "Description is required"),
     price: z.number().positive("Price must be positive"),
     location: z.string().min(1, "Location is required"),
     bedrooms: z.number().int().min(1, "At least 1 bedroom required"),
     bathrooms: z.number().int().min(1, "At least 1 bathroom required"),
     area: z.number().positive("Area must be positive"),
     images: z.array(z.string()).min(1).max(5),
   })
   export type PropertyFormValues = z.infer<typeof propertySchema>
   ```

### property-form.tsx 迁移

1. 移除 `useState` 手写校验逻辑（`errors` state、`validate()`、重复的 `newErrors` 块）
2. 导入 `useForm` from `react-hook-form`，`zodResolver` from `@hookform/resolvers/zod`，`propertySchema` / `PropertyFormValues` from `@/lib/schemas/property`
3. 导入 shadcn Form 组件：`Form`、`FormField`、`FormItem`、`FormLabel`、`FormControl`、`FormMessage` from `@/components/ui/form`
4. 导入 shadcn `Input`、`Textarea`、`Button` from `@/components/ui/`
5. 使用 `useForm<PropertyFormValues>({ resolver: zodResolver(propertySchema), defaultValues: { ... } })` 替代 `useState<AdminPropertyCreate>`
6. `useEffect` 中用 `form.reset(initialValues)` 替代 `setFormData`
7. 表单结构用 `<Form {...form}><form onSubmit={form.handleSubmit(onSubmit)}>` 包裹
8. 每个字段用 `<FormField control={form.control} name="..." render={({ field }) => ...}>` 包裹
9. 提交时将 `PropertyFormValues` 转换为 `AdminPropertyCreate`（images 过滤空字符串）再调用 `onSubmit`
10. **保留全部 F10 上传逻辑**：`uploadingIndex`、`fileInputRef`、`pendingUploadIndexRef`、`triggerUpload`、`handleFileChange`、隐藏 `<input type="file">`、Upload 按钮（含禁用逻辑）
11. 提交按钮改用 shadcn `Button`，保留 `disabled={form.formState.isSubmitting || uploadingIndex !== null}` 逻辑
12. `formError`（服务端错误）保留为独立 `useState<string | null>`，不纳入 Zod schema
13. `docker compose exec frontend npx tsc --noEmit` exit 0，不修改任何其他文件

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
