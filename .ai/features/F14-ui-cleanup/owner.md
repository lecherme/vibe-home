# F14 UI Cleanup — Ownership Boundaries

This is a static ownership map. Runtime state comes from `status.json`.

---

## T01（Gemini）— 迁移 PaginationControls 和 NavBar

**允许修改的文件：**
- `frontend/components/features/common/PaginationControls.tsx`
- `frontend/components/features/properties/NavBar.tsx`

**不得修改：** `frontend/app/`、`frontend/lib/`（只读）、`frontend/types/`（只读）、`backend/`、`status.json`

**强制约束：**
- **Button 样式显式写**：不依赖 shadcn CSS 变量，所有 className 用具体 Tailwind class
- PaginationControls 的 Previous/Next/Go Button 保留 outline/slate 风格（不换成 indigo）
- NavBar Sign out Button 保留 ghost/text 风格（不换成 indigo）
- 保留 PaginationControls 全部逻辑（pageInput、useEffect、clampPage、goToPage、handleSubmit、handleKeyDown）
- 保留 NavBar handleSignOut 完整逻辑

---

## T02（Codex）— Review

只读审查，不得修改任何源文件。输出 review report 到 stdout，由 harness 写入 `review.md`。

---

## T03（Claude）— Acceptance

Claude 写 `final-report.md` 并更新 `status.json`。

**允许修改的文件：**
- `.ai/features/F14-ui-cleanup/status.json`
- `.ai/features/F14-ui-cleanup/final-report.md`

---

## Boundary Rules（全阶段适用）

1. Workers 不得修改 `status.json`。
2. Workers 不得直接创建报告文件；harness 脚本负责将 stdout 写入 artifact。
3. Workers 不得修改当前任务 scope 之外的文件。
4. `frontend/app/` 页面文件在本 feature 中不得修改。
5. 不修改 `backend/` 任何文件。
6. **Button 样式显式写**：`globals.css` 无 shadcn CSS 变量，所有 Button className 必须用具体 Tailwind class。
7. **视觉不变原则**：迁移后按钮视觉效果必须与迁移前一致，不得借机调整颜色或尺寸。
