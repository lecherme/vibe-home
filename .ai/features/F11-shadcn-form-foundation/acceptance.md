# F11 shadcn/ui Form Foundation — Acceptance Criteria

## A1 — 依赖安装完整
`frontend/package.json` 包含 `zod`、`react-hook-form`、`@hookform/resolvers`、`lucide-react` 及所需 `@radix-ui/*` 包。

## A2 — shadcn 基础组件存在
`frontend/components/ui/` 下存在：`button.tsx`、`input.tsx`、`textarea.tsx`、`select.tsx`、`dialog.tsx`、`table.tsx`、`toast.tsx`（或 `use-toast.ts`）、`form.tsx`、`label.tsx`。

## A3 — property-form 使用 shadcn Form + react-hook-form
`property-form.tsx` 使用 `useForm` + `<Form>`、`<FormField>`、`<FormItem>`、`<FormControl>`、`<FormMessage>` 结构，手写 `useState` 校验逻辑已移除。

## A4 — Zod schema 覆盖所有字段
存在 Zod schema 覆盖 8 个字段（title、description、price、location、bedrooms、bathrooms、area、images），校验规则与原有逻辑等价（title 必填、price > 0、bedrooms ≥ 1、bathrooms ≥ 1、area > 0）。

## A5 — 上传功能不退化
Upload 按钮、`fileInputRef`、`triggerUpload`、`handleFileChange`、`uploadingIndex` 均保留；上传中按钮和提交按钮禁用；上传成功后 URL 填入对应字段。

## A6 — 图片数组交互保留
Add（最多 5 张）、Remove（至少 1 张）、Upload 三个操作均正常工作。

## A7 — tsc 通过
`docker compose exec frontend npx tsc --noEmit` exit 0。

## A8 — Admin 新增属性 happy path 通过
填写所有必填字段 → 提交 → 属性出现在列表。

## A9 — Admin 编辑属性 happy path 通过
编辑已有属性 → 修改字段 → 保存 → 更新结果正确反映在详情页。

## A10 — 其他页面未改动
`frontend/app/`、`frontend/lib/`、`frontend/components/features/`（除 `property-form.tsx`）无修改。
