# F11 — shadcn/ui Form Foundation

**Status:** in_progress  
**Created:** 2026-06-04

## Goal

建立 shadcn/ui + react-hook-form + Zod 的可复用表单模式。用 `property-form.tsx` 作为第一个迁移目标，验证三件事：shadcn Form 组件、react-hook-form 状态管理、Zod schema 验证。其他页面不动。

## Scope

### In scope
- 安装运行时依赖：`zod`、`react-hook-form`、`@hookform/resolvers`、`lucide-react`
- 通过 `npx shadcn add` 安装基础组件：`button`、`input`、`textarea`、`select`、`dialog`、`table`、`toast`、`form`、`label`
- 将 `frontend/components/features/admin/property-form.tsx` 迁移为 shadcn Form + react-hook-form + Zod
- 保留 F10 上传功能（Upload 按钮、fileInputRef、triggerUpload、handleFileChange、uploadingIndex 状态）
- 保留图片数组交互（最多 5 张、Add/Remove/Upload）

### Out of scope
- 其他任何页面或组件的 UI 替换
- 全站 Button/Input 迁移
- shadcn Dialog 替换现有删除确认 UI（留 F12）
- Toast 接入（组件装好即可，不接业务逻辑）
- 新增功能或视觉重设计

## Constraints

- `tsc --noEmit` 必须通过
- admin 新增属性 happy path 手测通过
- admin 编辑属性 happy path 手测通过
- 上传功能不退化（与 F10 验收标准一致）
- 不修改 `backend/` 任何文件
- 不修改 `frontend/lib/api/`、`frontend/lib/auth/`、`frontend/app/`
