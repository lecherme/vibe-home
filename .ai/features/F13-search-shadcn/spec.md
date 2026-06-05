# F13 — Search & Filter Components shadcn/ui Migration

**Status:** in_progress
**Created:** 2026-06-05

## Goal

将 `filter-panel.tsx` 和 `search-bar.tsx` 迁移至 shadcn/ui 组件，与 F11/F12 建立的模式一致。

## Scope

### In scope
- `frontend/components/features/search/filter-panel.tsx`：
  - 原生 `<label>` → shadcn `Label`
  - 原生 `<input type="number">` → shadcn `Input`
  - 原生 `<select>` → shadcn `Select`（SelectTrigger / SelectContent / SelectItem）
  - 保留全部 debounce 逻辑、local state、useRef、useEffect

- `frontend/components/features/search/search-bar.tsx`：
  - 原生 `<input type="text">` → shadcn `Input`（保留 `pl-10` search icon padding）
  - 原生 `<button>` → shadcn `Button`
  - 保留 onKeyDown、isLoading、search icon SVG

### Out of scope
- `frontend/app/` 页面文件
- `frontend/lib/`
- `frontend/types/`
- `backend/`
- 任何其他组件

## Constraints

- `tsc --noEmit` 必须通过
- 手测：搜索 happy path（输入关键词 → Enter / Search 按钮 → 结果显示）
- 手测：filter happy path（min/max price debounce、bedrooms/bathrooms/status select → 结果更新）
- 手测：Clear Filters 正常
- 手测：isLoading 期间所有 inputs/selects/button 禁用
- 不修改 `backend/` 任何文件
- Button 颜色必须用显式 Tailwind class（`bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50`）
