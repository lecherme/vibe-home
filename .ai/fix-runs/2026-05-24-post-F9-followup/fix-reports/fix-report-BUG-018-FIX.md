# Fix Report: BUG-018-FIX

## Ticket Info
- **Review Task:** open-bugs.md
- **Affected Task:** Admin — BUG-018 — Admin properties table overlaps on tablet/narrow viewport
- **Criterion:** BUG-018
- **Files Declared:** frontend/app/(dashboard)/admin/properties/page.tsx

## Files Changed
- frontend/app/(dashboard)/admin/properties/page.tsx

## Patch Summary
Worker 初版加了 `min-w-[780px]` + `min-w-[160px]`，实测仍不足。Claude fallback（BUG-018-FIX scope 内）进一步调整：table 改为 `min-w-[1024px]`；Property `<th>` 改为 `w-64`；Property `<td>` 去掉 `whitespace-nowrap`，加 `max-w-0`，flex 容器加 `min-w-0`，title/description 加 `truncate`；Location `<td>` 同样改为 `max-w-0 w-52` + text `truncate`。iPad 768px 以下由 `overflow-x-auto` 触发横向滚动，1024px 以上列宽正常分配。

## Open Issues
None.

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec frontend npx tsc --noEmit` | 无输出 | **PASS — exit 0** |
| 手动复测 iPad viewport | 列不再重叠；窄屏触发横向滚动；title/location 过长时 truncate 正常；Edit/Delete 完整可见 | **PASS — 2026-05-28** |
