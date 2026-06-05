# F13 Search & Filter shadcn/ui Migration — Ownership Boundaries

This is a static ownership map. Runtime state comes from `status.json`.

---

## T01（Gemini）— 迁移 filter-panel 和 search-bar

**允许修改的文件：**
- `frontend/components/features/search/filter-panel.tsx`
- `frontend/components/features/search/search-bar.tsx`

**不得修改：** `frontend/app/`、`frontend/lib/`（只读）、`frontend/types/`（只读）、`backend/`、`status.json`

**强制约束：**
- shadcn `Select` 使用 `onValueChange(value: string)` 而非原生 `onChange`；`disabled` prop 加在 `SelectTrigger` 上
- `Input` 保留原有的 `className` 额外 class（如 `pl-10` for search icon）
- **Button 样式显式写**：`bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50`
- 保留 filter-panel 全部 debounce 逻辑（`localMinPrice`、`localMaxPrice`、`priceDebounceTimers` ref、useEffect guard）
- 保留 search-bar 的 `onKeyDown` Enter 触发、search icon SVG、`isLoading` 文字切换

---

## T02（Codex）— Review

只读审查，不得修改任何源文件。输出 review report 到 stdout，由 harness 写入 `review.md`。

---

## T03（Claude）— Acceptance

Claude 写 `final-report.md` 并更新 `status.json`。

**允许修改的文件：**
- `.ai/features/F13-search-shadcn/status.json`
- `.ai/features/F13-search-shadcn/final-report.md`

---

## Boundary Rules（全阶段适用）

1. Workers 不得修改 `status.json`。
2. Workers 不得直接创建报告文件；harness 脚本负责将 stdout 写入 artifact。
3. Workers 不得修改当前任务 scope 之外的文件。
4. `frontend/app/` 页面文件在本 feature 中不得修改。
5. 不修改 `backend/` 任何文件。
6. **Button 样式显式写**：`globals.css` 无 shadcn CSS 变量，所有 Button 颜色必须用显式 Tailwind class（`bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50`）。
7. **Select disabled**：`disabled` prop 放在 `SelectTrigger` 上，不放在 `Select` 根组件。
8. **debounce 保留**：filter-panel 的价格 debounce 逻辑不得删除或简化。
