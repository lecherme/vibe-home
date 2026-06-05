# F13 Acceptance Criteria

## Build (T01)

| ID | Criterion |
|----|-----------|
| A1 | filter-panel: `Label` 替换原生 `<label>` |
| A2 | filter-panel: `Input` 替换 min/max price 的原生 `<input>` |
| A3 | filter-panel: `Select` 替换 bedrooms 原生 `<select>`；sentinel `"any"` → `undefined` |
| A4 | filter-panel: `Select` 替换 bathrooms 原生 `<select>`；sentinel `"any"` → `undefined` |
| A5 | filter-panel: `Select` 替换 status 原生 `<select>`；sentinel `"any"` → `undefined` |
| A6 | filter-panel: `disabled` 放在 `SelectTrigger` 上（不在 `Select` 根） |
| A7 | filter-panel: debounce 逻辑完整保留（localMinPrice/Max、priceDebounceTimers、filtersRef、两个 useEffect） |
| A8 | search-bar: `Input` 替换原生 `<input>`，保留 `pl-10` className 和 search icon SVG |
| A9 | search-bar: `Button` 替换原生 `<button>`，颜色显式 Tailwind（bg-indigo-600 等） |
| A10 | search-bar: `onKeyDown` Enter 触发保留 |
| A11 | `tsc --noEmit` exit 0 |

## Manual (T03 Claude)

| ID | Criterion |
|----|-----------|
| A12 | 搜索 happy path：输入关键词 → Enter → 结果显示 |
| A13 | 搜索 happy path：输入关键词 → Search 按钮 → 结果显示 |
| A14 | filter happy path：min/max price debounce → 结果更新（500ms 后） |
| A15 | filter happy path：bedrooms select → 结果更新 |
| A16 | filter happy path：bathrooms select → 结果更新 |
| A17 | filter happy path：status select → 结果更新 |
| A18 | Clear Filters 正常（重置所有 filter，重新搜索） |
| A19 | isLoading 期间：Input/Button/SelectTrigger 全部禁用 |
