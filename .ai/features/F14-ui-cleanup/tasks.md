# F14 UI Cleanup — Tasks

---

## T01 — Gemini: 迁移 PaginationControls 和 NavBar

- **owner:** gemini
- **type:** build
- **depends_on:** none
- **allowed files:**
  - `frontend/components/features/common/PaginationControls.tsx`
  - `frontend/components/features/properties/NavBar.tsx`

**Requirements:**

通用要求：
- 导入 shadcn `Button` from `@/components/ui/button`
- 导入 shadcn `Input` from `@/components/ui/input`
- 导入 shadcn `Label` from `@/components/ui/label`
- **Button className 必须显式写**，不依赖 shadcn CSS 变量
- 不修改任何其他文件

### PaginationControls.tsx

当前原生元素：
- `<button>` Previous：`className="px-4 py-2 border border-slate-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors"`
- `<button>` Next：同上
- `<button type="submit">` Go：同上
- `<input type="number">`：`className="w-20 rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"`
- `<label className="sr-only">`：screen-reader only label

迁移要求：
1. Previous / Next / Go → shadcn `Button`，保留原有 className（slate outline 风格，**不换成 indigo**）：
   ```tsx
   <Button
     type="button"
     onClick={() => onPageChange(page - 1)}
     disabled={page <= 1 || isLoading}
     className="px-4 py-2 border border-slate-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors"
   >
     Previous
   </Button>
   ```
2. `<input type="number">` → shadcn `Input`，保留原有 className：
   ```tsx
   <Input
     id="go-to-page"
     type="number"
     value={pageInput}
     onChange={(event) => setPageInput(event.target.value)}
     onKeyDown={handleKeyDown}
     disabled={isLoading}
     className="w-20 rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
   />
   ```
3. `<label className="sr-only">` → shadcn `Label`：
   ```tsx
   <Label htmlFor="go-to-page" className="sr-only">
     Go to page
   </Label>
   ```
4. **完整保留所有逻辑**：`pageInput` state、`useEffect`（page sync）、`clampPage`、`goToPage`、`handleSubmit`、`handleKeyDown`

### NavBar.tsx

当前原生元素：
- `<button onClick={handleSignOut}>` Sign out：`className="rounded-md px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-900"`

迁移要求：
1. Sign out → shadcn `Button`，保留原有 className（ghost/text 风格，**不换成 indigo**）：
   ```tsx
   <Button
     onClick={handleSignOut}
     className="rounded-md px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-900"
   >
     Sign out
   </Button>
   ```
2. 保留 `handleSignOut` 完整逻辑（`signOut()`、`router.refresh()`、`router.push("/login")`、try/catch）

### Required Fix（retry 原因）

T02 Codex review FAIL：shadcn Button 默认 variant 注入 `bg-primary text-primary-foreground h-10`，这些 class 必须被显式覆盖。

对 **PaginationControls 的 3 个 Button**（Previous、Next、Go）className 补加：
- `bg-white text-slate-700 h-auto` — 覆盖 `bg-primary text-primary-foreground h-10`

对 **NavBar 的 Sign out Button** className 补加：
- `bg-transparent h-auto` — 覆盖 `bg-primary h-10`；`text-slate-600` 已在 className 中，无需重复

修复后各 Button 的最终 className 示例：

```tsx
// PaginationControls — Previous
className="bg-white text-slate-700 h-auto px-4 py-2 border border-slate-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors"

// NavBar — Sign out
className="bg-transparent h-auto rounded-md px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-900"
```

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
