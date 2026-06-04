# F11 shadcn/ui Form Foundation — Claude Acceptance Report (T04)

**Date:** 2026-06-04  
**Reviewer:** Claude (T04 acceptance owner)

## Disposition: ACCEPTED

---

## Feature Summary

F11 建立了 shadcn/ui + react-hook-form + Zod 的可复用表单模式，以 `property-form.tsx` 为第一个迁移目标：

- **T01 (Codex):** 安装依赖（zod、react-hook-form、@hookform/resolvers、lucide-react）及 shadcn 基础组件（button、input、textarea、select、dialog、table、toast、form、label）。首次因 `hooks/use-toast.ts` 超出 scope 失败，补充 `frontend/hooks/*` 后通过。
- **T02 (Gemini):** 将 `property-form.tsx` 迁移为 shadcn Form + react-hook-form + Zod，新建 `frontend/lib/schemas/property.ts`，保留 F10 上传逻辑。
- **T03 (Codex review, 2 runs):** 第一次 FAIL（A4 trim 缺失、A8/A9 无手测记录）。Fix loop 修复后第二次 PASS，全部 12 条通过。
- **T04 (Claude):** 本报告。

**Fix loop 修复项（T03 FAIL 后）：**
- A4：`title`/`description`/`location` 加 `.trim()` 防空格绕过
- 运行时：`FormLabel` 用在 `FormField` 外触发 React context 错误 → 改为普通 `<label>`
- UX：数字字段 `value={field.value || ""}` 防止 `0` 遮挡输入
- A5：图片上传回显改为 `form.setValue(\`images.${index}\`)` 精确更新对应字段
- UX：Save 按钮加显式蓝色（`globals.css` 无 shadcn CSS 变量）

---

## Criteria Results (from T03 review.md — final PASS run)

| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 — 依赖安装完整 | PASS | zod、react-hook-form、@hookform/resolvers、lucide-react、@radix-ui/* 均在 package.json |
| A2 — shadcn 基础组件存在 | PASS | components/ui/ 下 9 个组件 + hooks/use-toast.ts |
| A3 — property-form 使用 shadcn Form + react-hook-form | PASS | useForm + FormField/FormItem/FormControl/FormMessage，手写 validate 已移除 |
| A4 — Zod schema 覆盖所有字段 | PASS | 8 字段覆盖，string 字段加 .trim() |
| A5 — 上传功能不退化 | PASS | F10 全部上传逻辑保留，URL 回显修复 |
| A6 — 图片数组交互保留 | PASS | Add/Remove/Upload 均正常，max-5/min-1 守卫保留 |
| A7 — tsc 通过 | PASS | docker compose exec frontend npx tsc --noEmit exit 0 |
| A8 — Admin 新增属性 happy path 通过 | PASS | 用户手测通过（2026-06-04） |
| A9 — Admin 编辑属性 happy path 通过 | PASS | 用户手测通过（2026-06-04） |
| A10 — 其他页面未改动 | PASS | 仅改 property-form.tsx 和新建 lib/schemas/property.ts |

---

## Open Items

- **NOTE (non-blocking):** `globals.css` 无 shadcn CSS 变量，所有 shadcn Button 依赖 CSS 变量的颜色（variant default/secondary/outline）需显式 Tailwind class 补色。F12 auth 表单迁移时应一并处理，或考虑在 F12 中补充 globals.css 变量。

---

## Accepted
