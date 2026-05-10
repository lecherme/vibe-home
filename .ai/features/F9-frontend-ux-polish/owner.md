# Frontend UX Polish — Ownership Boundaries

This is a static ownership map. Runtime state comes from `status.json`.

---

## T01（审计阶段）

### Gemini（T01 owner）

T01 是只读审计任务。Gemini 被授权读取以下路径（但不得修改）：

- `frontend/app/` — 所有页面文件
- `frontend/components/` — 所有组件文件
- `frontend/lib/` — API 层、auth 层
- `frontend/middleware.ts`
- `frontend/types/`

Gemini 在 T01 期间唯一允许写入的文件：
- `.ai/features/F9-frontend-ux-polish/gemini-build-T01.md`（审计报告，由 harness 脚本捕获 stdout 写入）

### Codex

T01 期间无 Codex 任务，Codex 不得修改任何文件。

### Claude

Claude 在 T01 完成后评审 `gemini-build-T01.md`，决定第二阶段任务结构，并更新：
- `.ai/features/F9-frontend-ux-polish/tasks.md`（追加 T02+）
- `.ai/features/F9-frontend-ux-polish/acceptance.md`（追加第二阶段验收项）
- `.ai/features/F9-frontend-ux-polish/owner.md`（追加第二阶段边界）
- `.ai/features/F9-frontend-ux-polish/status.json`（更新任务列表和 activity_log）

---

---

## T02（Codex）

**允许修改的文件：**
- `frontend/lib/api/favorites.ts`
- `frontend/middleware.ts`

**不得修改：** `frontend/app/`、`frontend/components/`、`backend/`、`status.json`

> 注：`redirectTo` 参数的读取端（LoginForm.tsx）由 T05 的 Gemini 任务完成；T02 只负责 middleware 写入端。

---

## T03（Gemini）

**允许修改的文件：**
- `frontend/components/features/favorites/favorite-button.tsx`
- `frontend/app/(dashboard)/properties/[id]/page.tsx`
- `frontend/app/(dashboard)/properties/page.tsx`
- `frontend/app/(dashboard)/search/page.tsx`

**不得修改：** `frontend/lib/`、`frontend/middleware.ts`、`backend/`、`status.json`

---

## T04（Gemini）

**允许修改的文件：**
- `frontend/app/(dashboard)/search/page.tsx`
- `frontend/app/(dashboard)/properties/page.tsx`

**不得修改：** `frontend/lib/`、`frontend/middleware.ts`、`backend/`、`status.json`

---

## T05（Gemini）

**允许修改的文件：**
- `frontend/components/features/properties/NavBar.tsx`
- `frontend/components/features/auth/LoginForm.tsx`
- `frontend/app/(dashboard)/admin/properties/page.tsx`
- `frontend/components/features/admin/property-form.tsx`

**不得修改：** `frontend/lib/`、`frontend/middleware.ts`、`backend/`、`status.json`

---

## T06（Gemini）

**允许修改的文件：**
- `frontend/components/features/properties/PropertyCard.tsx`
- `frontend/components/features/properties/PropertyDetail.tsx`
- `frontend/app/(dashboard)/properties/page.tsx`
- `frontend/app/(dashboard)/search/page.tsx`
- `frontend/app/(dashboard)/favorites/page.tsx`
- `frontend/app/(dashboard)/admin/properties/page.tsx`

**不得修改：** `frontend/lib/`、`frontend/middleware.ts`、`backend/`、`status.json`

---

## T07（Codex review）

只读审查，不得修改任何源文件。写 `review.md`（由 harness 脚本捕获 stdout）。

---

## T08（Claude）

Claude 写 `final-report.md` 并更新 `status.json`。

---

## Boundary Rules（全阶段适用）

1. Workers 不得修改 `status.json`。
2. Workers 不得直接创建报告文件；harness 脚本负责将 stdout 写入 artifact。
3. Workers 不得修改当前任务 scope 之外的文件。
4. `frontend/app/` 和 `frontend/components/` 中不得出现直接 `fetch()` 调用。
5. Supabase 相关 import 只允许在 `frontend/lib/auth/` 中出现。
