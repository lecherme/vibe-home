# Fix Report: OBS-007-FIX

## Ticket Info
- **Review Task:** open-bugs.md
- **Affected Task:** Search — OBS-007 — 价格输入无 debounce，loading 期间阻断输入
- **Criterion:** OBS-007
- **Files Declared:** frontend/components/features/search/filter-panel.tsx, frontend/app/(dashboard)/search/page.tsx

## Files Changed
- frontend/components/features/search/filter-panel.tsx
- frontend/app/(dashboard)/search/page.tsx

## Patch Summary
`filter-panel.tsx`：为 min/max price 引入 local state，500ms debounce via `useRef` timer；`useEffect` 在父级 filters 变化时同步 local state（带 debounce 活跃 guard，防止 typing 期间其他 filter 变化覆盖用户输入）；price inputs 保留 `disabled={isLoading}`（保守方案，避免并发请求 race condition）；selects 行为不变。`search/page.tsx`：loading overlay 加 `pointer-events-none`。OBS-010 记录到 next-iteration backlog，待未来允许 loading 期间改筛选时补 request ID guard。

## Open Issues
None.

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec frontend npx tsc --noEmit` | 无输出 | **PASS — exit 0** |
| 手动复测 | 慢速输入不触发多次搜索；停止 500ms 后触发一次；切换 bedrooms 时 price 不被清空；Clear Filters 正常清空；loading 期间全部 inputs 锁住 | **PASS — 2026-05-27** |
