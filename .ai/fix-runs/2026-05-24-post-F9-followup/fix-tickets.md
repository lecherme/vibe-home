# Fix Tickets — 2026-05-24 post-F9 followup

Standalone fix batch for bugs from the post-F9 QA run backlog.
Source: `.ai/bugs/open-bugs.md`

---

## BUG-013-FIX

- **Bug:** BUG-013 — 生产环境 API URL 无 fallback，部署风险
- **Owner:** Codex
- **Severity:** P2 / Medium
- **Allowed files:**
  1. `frontend/lib/api/config.ts` ← 新建
  2. `frontend/lib/api/properties.ts`
  3. `frontend/lib/api/auth.ts`
  4. `frontend/lib/api/favorites.ts`
  5. `frontend/lib/api/admin.ts`
  6. `frontend/lib/api/health.ts`
- **Requirements:**
  1. 新建 `frontend/lib/api/config.ts`，内容如下（不多不少）：
     ```ts
     const apiUrl = process.env.NEXT_PUBLIC_API_URL;
     if (!apiUrl) throw new Error("NEXT_PUBLIC_API_URL is not configured");
     export { apiUrl };
     ```
  2. `properties.ts`、`auth.ts`、`favorites.ts`、`admin.ts`：删除各自的 `const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"`，改为 `import { apiUrl } from "@/lib/api/config"`
  3. `health.ts`：删除函数内 inline 的 `const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"`，改为在文件顶部 `import { apiUrl } from "@/lib/api/config"`
  4. 5 个 api 文件不得保留任何 `localhost:8000` 字符串或独立 `NEXT_PUBLIC_API_URL` 读取
  5. error message 必须为：`NEXT_PUBLIC_API_URL is not configured`
  6. 不修改其他任何文件
  7. tsc 通过
- **Verification:** `docker compose exec frontend npx tsc --noEmit` exit 0
- **Status:** verified — tsc exit 0；无 localhost:8000 残留（2026-05-24）

---

## BUG-016-FIX

- **Bug:** BUG-016 — Root route / 显示 HealthPage 而非角色跳转
- **Owner:** Codex
- **Severity:** P2 / Medium
- **Allowed files:**
  1. `frontend/middleware.ts`
  2. `frontend/app/page.tsx`
  3. `frontend/app/health/page.tsx` ← 新建
- **Requirements:**
  1. `frontend/middleware.ts`：在 `if (session)` 块内，`pathname === "/"` 时按角色跳转：user → `/properties`，admin → `/admin/properties`；使用已有的 `getRoleFromSession` 和 `getDefaultPage`
  2. `frontend/app/page.tsx`：移除 HealthPage 内容，改为 `redirect("/login")` 兜底（server component，import `redirect` from `next/navigation`）
  3. `frontend/app/health/page.tsx`（新建）：迁移原 HealthPage 全部内容，保留健康检查功能不变
  4. 不修改其他任何文件
  5. tsc 通过
- **Verification:** `docker compose exec frontend npx tsc --noEmit` exit 0
- **Status:** verified — tsc exit 0；手动复测全 PASS（2026-05-25）

---

## BUG-012-FIX

- **Bug:** BUG-012 — Admin 表单 image_url（string）与 Property 类型 images（array）不一致
- **Owner:** Codex
- **Severity:** P3 / Low
- **Allowed files:**
  1. `backend/app/schemas/admin.py`
  2. `backend/app/services/admin/service.py`
  3. `frontend/types/admin.ts`
  4. `frontend/components/features/admin/property-form.tsx`
  5. `frontend/app/(dashboard)/admin/properties/[id]/edit/page.tsx`
- **Requirements:**
  1. `backend/app/schemas/admin.py`：`PropertyCreate.images` 改为 `images: list[str] = Field(default_factory=list)`；`PropertyUpdate.images` 改为 `images: Optional[list[str]] = None`；若文件未 import `Field`，则补 `from pydantic import Field`；删除旧的 `image_url` 字段
  2. `backend/app/services/admin/service.py`：删除 `_build_images()` 函数；`create_property` 直接使用 `data.images`；`update_property` 改为 `if "images" in updates` 更新 `updated_values["images"]`；不再引用 `image_url`
  3. `frontend/types/admin.ts`：`image_url: string` → `images: string[]`；`AdminPropertyUpdate extends Partial<AdminPropertyCreate>`，无需单独修改
  4. `frontend/components/features/admin/property-form.tsx`：将单个 `image_url` text input 替换为动态 URL 列表；初始 1 个输入框；Add Image URL 按钮（最多 5 个）；每行有 Remove 按钮（只剩 1 个时 disabled）；提交前过滤空字符串；允许 `images: []`；不校验 URL 格式
  5. `frontend/app/(dashboard)/admin/properties/[id]/edit/page.tsx`：加载时将 `image_url: property.images[0] ?? ""` 改为 `images: property.images ?? []`
  6. 不修改其他任何文件；不实现文件上传
  7. tsc 通过；`docker compose exec backend python -c "from app.services.admin.service import create_property"` exit 0
- **Verification:** `docker compose exec frontend npx tsc --noEmit` exit 0；`docker compose exec backend python -c "from app.services.admin.service import create_property"` exit 0
- **Status:** verified — 手动复测全 PASS（2026-05-26）

---

## BUG-010-FIX

- **Bug:** BUG-010 — Favorites 分页缺失 + ghost unfavorited
- **Owner:** Codex
- **Severity:** P2 / Medium
- **Allowed files:**
  1. `frontend/app/(dashboard)/favorites/page.tsx`
  2. `frontend/lib/api/favorites.ts`
  3. `frontend/app/(dashboard)/search/page.tsx`
- **Requirements:**
  1. `favorites.ts`：新增 `getAllFavoriteIds()` 函数，每页请求 `page_size=50`（尊重后端 MAX_PAGE_SIZE=50），循环条件 `(page - 1) * 50 < total`，返回 `Set<string>`，包含该用户所有已收藏的 property id。
  2. `search/page.tsx`：将 `favoritesApi.getFavorites(1, 100)` 替换为 `favoritesApi.getAllFavoriteIds()`；收藏拉取失败时继续静默降级为空集合（`new Set()`），不阻断搜索结果渲染。
  3. `favorites/page.tsx`：
     - 增加 `page` state（初始值从 URL `?page=` 读取，fallback 1）和 `total` state（初始值 0）；`PAGE_SIZE = 12`（与现有默认一致）
     - `page` 变化时同步写入 URL searchParam（`?page=N`），使用 `useRouter` + `useSearchParams`；刷新后从 URL 恢复页码
     - 调用 `favoritesApi.getFavorites(page, PAGE_SIZE)` 并更新 `total`；`useEffect` 依赖 `page`
     - 在卡片列表下方加 Previous/Next 分页 UI：`page <= 1` 时 Previous disabled，`page >= totalPages` 时 Next disabled；`totalPages = Math.ceil(total / PAGE_SIZE)`；`totalPages <= 1` 时不渲染分页区
     - 取消收藏后：若当前页 favorites 数量 > 1 则刷新当前页；若当前页只剩 1 条且 `page > 1` 则跳到 `page - 1`（与 BUG-011-FIX 边界逻辑一致）
  4. 不修改其他任何文件；不改后端代码
  5. tsc 通过
- **Verification:** `docker compose exec frontend npx tsc --noEmit` exit 0
- **Status:** verified — 手动复测全 PASS（2026-05-26）

---

## BUG-011-FIX

- **Bug:** BUG-011 — Admin 房源列表无分页
- **Owner:** Codex
- **Severity:** P2 / Medium
- **Allowed files:**
  - `frontend/app/(dashboard)/admin/properties/page.tsx`
- **Requirements:**
  1. 增加 `page` state（初始值从 URL searchParam `?page=` 读取，fallback 1）和 `total` state（初始值 0）；定义 `PAGE_SIZE = 20`
  2. `page` state 变化时同步写入 URL searchParam（`?page=N`），使用 `useRouter` + `useSearchParams`；刷新后从 URL 恢复页码
  3. `fetchProperties` 改为接收 `page` 参数，调用 `propertiesApi.list(page, PAGE_SIZE)`，同时更新 `total` state；`useEffect` 依赖 `page` 变化触发重新请求
  4. 在表格下方加 Previous/Next 分页 UI（与 properties/page.tsx 风格一致）：`page <= 1` 时 Previous disabled，`page >= totalPages` 时 Next disabled；`totalPages = Math.ceil(total / PAGE_SIZE)`；`totalPages <= 1` 时不渲染分页区
  5. 删除逻辑（`handleDelete`）：边界情况（当前页只剩 1 条且 `page > 1`）时，不做乐观移除，`setDeletingId(null)` 移到 `finally`，删除期间保持 deleting 状态；成功后调用 `updatePage(page - 1)` 跳页；空状态条件加 `deletingId === null` 守卫，防止闪现"No properties yet"。非边界情况：成功后乐观过滤并刷新当前页。（Claude 授权 fallback 修复，2026-05-25）
  6. 修复 Actions 列（Edit/Delete）overflow 截断：改用 `w-full table-fixed` 表格布局，`th`/`td` 明确列宽（Location `w-52`、Price `w-36`、Status `w-28`、Actions `w-40 whitespace-nowrap`），内容用 `inline-flex gap-4`；1440px 桌面下 Edit/Delete 完整可见，无需水平滚动。（Claude 授权 fallback 修复，2026-05-25）
  7. "Add Property" 链接保持不变（`href="/admin/properties/new"`）；编辑链接保持不变（`href=\`/admin/properties/${id}/edit\``）；不需要改路由，回来后从 URL 恢复当前页
  8. 不修改其他任何文件
  9. tsc 通过
- **Verification:** `docker compose exec frontend npx tsc --noEmit` exit 0
- **Status:** verified — 手动复测全 PASS（2026-05-25）
