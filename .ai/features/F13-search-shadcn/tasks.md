# F13 Search & Filter shadcn/ui Migration — Tasks

---

## T01 — Gemini: 迁移 filter-panel 和 search-bar

- **owner:** gemini
- **type:** build
- **depends_on:** none
- **allowed files:**
  - `frontend/components/features/search/filter-panel.tsx`
  - `frontend/components/features/search/search-bar.tsx`

**Requirements:**

通用要求：
- 导入 shadcn `Input` from `@/components/ui/input`
- 导入 shadcn `Button` from `@/components/ui/button`
- 导入 shadcn `Label` from `@/components/ui/label`
- 导入 `Select`、`SelectTrigger`、`SelectValue`、`SelectContent`、`SelectItem` from `@/components/ui/select`
- **Button 颜色显式写**：`bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50`，不依赖 shadcn CSS 变量
- 不修改任何其他文件

### filter-panel.tsx

1. 原生 `<label>` → shadcn `Label`（保留 `htmlFor`）
2. Min Price / Max Price：原生 `<input type="number">` → shadcn `Input`；保留 `type="number"`、`value`、`onChange`、`placeholder`、`disabled={isLoading}`；保留原有 className
3. Min Bedrooms / Min Bathrooms / Status：原生 `<select>` → shadcn `Select` 组合：
   ```tsx
   <Select
     value={filters.bedrooms?.toString() ?? "any"}
     onValueChange={(val) =>
       handleChange("bedrooms", val === "any" ? undefined : Number(val))
     }
   >
     <SelectTrigger disabled={isLoading}>
       <SelectValue />
     </SelectTrigger>
     <SelectContent>
       <SelectItem value="any">Any</SelectItem>
       {[1, 2, 3, 4, 5].map((num) => (
         <SelectItem key={num} value={String(num)}>{num}+ beds</SelectItem>
       ))}
     </SelectContent>
   </Select>
   ```
   - bathrooms 同理（`{num}+ baths`）
   - status：
     ```tsx
     <Select
       value={filters.status ?? "any"}
       onValueChange={(val) =>
         handleChange("status", val === "any" ? undefined : val)
       }
     >
       <SelectTrigger disabled={isLoading}><SelectValue /></SelectTrigger>
       <SelectContent>
         <SelectItem value="any">Any Status</SelectItem>
         <SelectItem value="available">Available</SelectItem>
         <SelectItem value="sold">Sold</SelectItem>
         <SelectItem value="rented">Rented</SelectItem>
       </SelectContent>
     </Select>
     ```
   - **`disabled` 放在 `SelectTrigger` 上，不放在 `Select` 根组件**
4. **完整保留全部 debounce 逻辑**：
   - `localMinPrice` / `localMaxPrice` state
   - `priceDebounceTimers` ref
   - `filtersRef` ref
   - 两个 `useEffect`（filters sync + cleanup）
   - `handlePriceChange` 函数
5. 整体结构（`rounded-lg border` 容器、`grid` 布局、5 列）保持不变

### search-bar.tsx

1. 原生 `<input type="text">` → shadcn `Input`：
   - 保留 `type="text"`、`value`、`onChange`、`onKeyDown`（Enter 触发 `onSearch`）、`placeholder`、`disabled={isLoading}`
   - 保留 `pl-10` className（为左侧 search icon 留空间）
2. 原生 `<button>` → shadcn `Button`：
   - `onClick={onSearch}`、`disabled={isLoading}`
   - className：`bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 w-28 shrink-0`
   - 文字：`{isLoading ? "Searching..." : "Search"}`
3. Search icon SVG 保留在 `Input` 左侧（`relative div` + `absolute pointer-events-none` 定位，与现在一致）

**Verification（worker 只需确认 tsc）：**

```bash
docker compose exec frontend npx tsc --noEmit
```

exit 0 即通过。

---

## T02 — Codex: review

- **owner:** codex
- **type:** review
- **depends_on:** T01

Review against acceptance.md criteria。只读，不修改源文件。

---

## T03 — Claude: acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T02
