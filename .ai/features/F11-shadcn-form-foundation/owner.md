# shadcn/ui Form Foundation — Ownership Boundaries

This is a static ownership map. Runtime state comes from `status.json`.

---

## T01（Codex）— 安装依赖和 shadcn 组件

**允许修改的文件：**
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/components/ui/*`（所有 shadcn 生成文件）

**不得修改：** `frontend/app/`、`frontend/components/features/`、`frontend/lib/`、`backend/`、`status.json`

---

## T02（Gemini）— 迁移 property-form.tsx

**允许修改的文件：**
- `frontend/components/features/admin/property-form.tsx`
- `frontend/lib/schemas/property.ts`（新建）

**不得修改：** `frontend/app/`、`frontend/lib/api/`、`frontend/lib/auth/`、`frontend/types/`（只读）、`backend/`、`status.json`

---

## T03（Codex）— Review

只读审查，不得修改任何源文件。输出 review report 到 stdout，由 harness 写入 `review.md`。

---

## T04（Claude）— Acceptance

Claude 写 `final-report.md` 并更新 `status.json`。

**允许修改的文件：**
- `.ai/features/F11-shadcn-form-foundation/status.json`
- `.ai/features/F11-shadcn-form-foundation/final-report.md`

---

## Boundary Rules（全阶段适用）

1. Workers 不得修改 `status.json`。
2. Workers 不得直接创建报告文件；harness 脚本负责将 stdout 写入 artifact。
3. Workers 不得修改当前任务 scope 之外的文件。
4. `frontend/app/` 和 `frontend/components/features/`（除 `property-form.tsx`）不得在本 feature 中修改。
5. 不修改 `backend/` 任何文件。
6. F10 上传功能（fileInputRef、triggerUpload、handleFileChange、uploadingIndex）必须完整保留，不得因表单重构退化。
