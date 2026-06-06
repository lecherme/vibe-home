# F14 — UI Cleanup / Remaining Primitive Controls Migration

**Status:** in_progress
**Created:** 2026-06-06

## Goal

收尾剩余未统一的原生 button/input/label，对齐 F11/F12/F13 建立的 shadcn/ui 模式。

## Scope

### In scope
- `frontend/components/features/common/PaginationControls.tsx`：
  - 3 个原生 `<button>` → shadcn `Button`（Previous、Next、Go）
  - 1 个原生 `<input type="number">` → shadcn `Input`
  - 1 个原生 `<label className="sr-only">` → shadcn `Label`
  - 保留全部逻辑：pageInput state、useEffect、clampPage、goToPage、handleSubmit、handleKeyDown

- `frontend/components/features/properties/NavBar.tsx`：
  - 1 个原生 `<button>`（Sign out）→ shadcn `Button`
  - 保留 handleSignOut、router.refresh、router.push 逻辑
  - 保留原有视觉样式（ghost/text 风格，slate 色）

### Out of scope
- `favorite-button.tsx`（icon-only，条件样式复杂，不适合强套 shadcn Button）
- `property-form.tsx`（F11 已处理）
- auth 表单（F12 已处理）
- search/filter 组件（F13 已处理）
- `frontend/app/` 页面文件
- `frontend/lib/`、`frontend/types/`、`backend/`

## Constraints

- `tsc --noEmit` 必须通过
- 手测：分页 Previous/Next/Go 行为不变
- 手测：NavBar Sign out 正常跳 /login
- Button 颜色必须与现有视觉一致，用显式 Tailwind class
- 不引入任何新功能或视觉重设计
