# Image Upload — Ownership Boundaries

This is a static ownership map. Runtime state comes from `status.json`.

---

## T01（Codex）— Backend upload endpoint

**允许修改的文件：**
- `backend/app/api/v1/admin/router.py`
- `backend/requirements.txt`

**不得修改：** `frontend/`、`backend/app/main.py`、`backend/tests/`、`status.json`

---

## T02（Gemini → Claude fallback）— Frontend upload UI

**允许修改的文件：**
- `frontend/lib/api/admin.ts`
- `frontend/components/features/admin/property-form.tsx`

> 注：Gemini worker 因网络故障（ECONNRESET）未能执行，由 Claude fallback 完成代码变更。

**不得修改：** `frontend/types/`（由 fix loop 追加）、`backend/`、`status.json`

---

## T03（Codex）— Review

只读审查，不得修改任何源文件。输出 review report 到 stdout，由 harness 写入 `review.md`。

**Fix loop 补充范围（经 Claude 授权）：**
- `frontend/types/admin.ts` — 发布 `PropertyImageUploadResponse`
- `frontend/components/features/admin/property-form.tsx` — A9 submit button fix

---

## T04（Claude）— Acceptance

Claude 写 `final-report.md` 并更新 `status.json`。

**允许修改的文件：**
- `.ai/features/F10-image-upload/status.json`
- `.ai/features/F10-image-upload/final-report.md`

---

## Boundary Rules（全阶段适用）

1. Workers 不得修改 `status.json`。
2. Workers 不得直接创建报告文件；harness 脚本负责将 stdout 写入 artifact。
3. Workers 不得修改当前任务 scope 之外的文件。
4. `frontend/app/` 和 `frontend/components/` 中不得出现直接 `fetch()` 调用；上传 transport 必须在 `frontend/lib/api/admin.ts` 中。
5. 不得从前端直接访问 Supabase Storage；上传必须经过后端 API。
