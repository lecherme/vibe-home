# Frontend UX Polish — Tasks

Every task has exactly one owner. Collaboration happens through sequential tasks, not shared tasks.

> **本 feature 分两阶段执行。**
> - **第一阶段**：T01 只读审计，产出 P0/P1/P2 分类问题清单
> - **第二阶段**：Claude 评审 T01 输出后，追加 T02+ 修复任务到本文件（不修改 T01）
>
> 当前仅定义第一阶段。

---

## T01 — Frontend UX Audit（只读审计）

- **owner:** gemini
- **type:** audit
- **depends_on:** none

**目标：** 系统性阅读所有前端代码，找出真实 bug（P0）、明显 UX 缺口（P1）、待打磨项（P2），输出分类问题清单。**不修改任何源文件。**

**审计范围：**

### 1. 收藏交互与状态同步
- `frontend/components/features/favorites/favorite-button.tsx`：409 错误处理、乐观更新回滚逻辑
- `frontend/app/(dashboard)/properties/[id]/page.tsx`：`isFavorite` 竞态窗口
- `frontend/app/(dashboard)/properties/page.tsx`、`search/page.tsx`：`isFavorited` prop 是否传入 `PropertyCard`
- `frontend/app/(dashboard)/favorites/page.tsx`：收藏页状态同步

### 2. 登录后 session / 权限跳转
- `frontend/middleware.ts`：未登录跳转规则、登录后 redirect 目标
- `frontend/lib/auth/session.ts`：token 过期行为
- 登录/注册页：错误提示、loading 状态、成功后跳转行为

### 3. 各页面 loading / empty / error state
- `/properties`、`/properties/[id]`、`/search`、`/favorites`、`/admin` 各页面
- 是否有 loading skeleton；empty state 是否存在及文案是否合理；error state 是否存在且含重试入口

### 4. 表单交互反馈
- 登录/注册表单：校验错误提示、提交 loading 禁用、成功/失败反馈
- Admin 新增/编辑房产表单：同上

### 5. 图片加载/降级
- `PropertyCard`、`PropertyDetail` 等组件中图片 `onError` 降级是否实现
- 无图片房源的展示行为

### 6. 分页/筛选/URL 状态
- 搜索/筛选参数是否反映在 URL（browser back / refresh 是否保留状态）
- 分页参数是否正常工作（如有分页组件）

### 7. 移动端/响应式
- 375px 下各页面关键组件布局是否合理（Tailwind 断点 sm/md/lg 使用情况）
- 导航/头部/卡片/表单的明显响应式问题

### 8. 文案、日期、货币格式一致性
- 价格展示格式是否统一
- 日期格式是否统一
- 英文/中文文案混用异常

**输出格式（gemini-build-T01.md）：**

```
## P0 — 真实 Bug（功能不正确或产生报错）
| # | 页面/组件 | 问题描述 | 受影响文件 |
...

## P1 — 明显 UX 缺口（功能缺失但不报错）
| # | 页面/组件 | 问题描述 | 受影响文件 |
...

## P2 — Polish（体验细节，不影响主流程）
| # | 页面/组件 | 问题描述 | 受影响文件 |
...
```

**Done condition:** `gemini-build-T01.md` 已写入，含 P0/P1/P2 分类问题清单，每条包含页面/组件名称、问题描述、受影响文件路径。T01 期间无任何源文件被修改。

---

> T01 已完成（2026-05-11），以下为 Claude 评审后追加的第二阶段修复任务。

---

## T02 — Codex：收藏错误类型 + 登录 redirect 保留

- **owner:** codex
- **type:** build
- **depends_on:** none

**Scope:**
- `frontend/lib/api/favorites.ts`
  - 新增并导出 `FavoriteConflictError extends Error` 类
  - `addFavorite` 在收到 HTTP 409 时抛出 `FavoriteConflictError`，其余错误仍抛泛型 `Error`
- `frontend/middleware.ts`
  - 未登录访问受保护路由时，将原始路径作为 `redirectTo` query param 附加到登录跳转 URL（例：`/login?redirectTo=/properties/123`）
  - 注意：读取 `redirectTo` 并跳回原页面的逻辑在 LoginForm（Gemini 所有），由 T05 完成；T02 只负责写入该参数

**Done condition:** `FavoriteConflictError` 已导出；`addFavorite` 对 409 抛该类型；middleware 登录跳转 URL 携带 `redirectTo` 参数；`tsc --noEmit` 通过。Artifact: `codex-build-T02.md`.

---

## T03 — Gemini：收藏链路前端修复

- **owner:** gemini
- **type:** build
- **depends_on:** T02

**Scope:**
- `frontend/components/features/favorites/favorite-button.tsx`
  - import `FavoriteConflictError`
  - catch 块：捕获 `FavoriteConflictError` 时将 `isFavorited` 置为 `true`，不 revert，不显示用户可见错误；其余错误仍 revert
- `frontend/app/(dashboard)/properties/[id]/page.tsx`
  - 增加 `isFavoriteLoaded` state（初始 `false`），`isFavorite` API resolve 后置 `true`
  - `FavoriteButton` 仅在 `isFavoriteLoaded === true` 后渲染；期间显示与按钮尺寸一致的骨架占位
- `frontend/app/(dashboard)/properties/page.tsx`
  - 挂载后获取当前用户收藏房源列表，构建 `Set<propertyId>`，传 `isFavorited` 给每个 `PropertyCard`
  - 收藏列表获取失败时降级为空 Set，不阻断主列表渲染
- `frontend/app/(dashboard)/search/page.tsx`
  - 同 properties/page.tsx：补充收藏状态同步

**Done condition:** `FavoriteButton` 对 409 静默处理；详情页无竞态闪烁；列表/搜索页收藏状态从后端同步；`tsc --noEmit` 通过。Artifact: `gemini-build-T03.md`.

---

## T04 — Gemini：搜索/URL 状态持久化

- **owner:** gemini
- **type:** build
- **depends_on:** T03

**Scope:**
- `frontend/app/(dashboard)/search/page.tsx`
  - 搜索关键词、筛选条件持久化到 URL query string（使用 `useSearchParams` / `useRouter`）
  - 页面刷新或浏览器后退后，从 URL 恢复筛选状态
  - 点击 "Clear filters" 后自动触发新一次搜索，不需要用户手动再点 Search
- `frontend/app/(dashboard)/properties/page.tsx`
  - 分页当前页码持久化到 URL（`?page=N`）；刷新后恢复当前页

**Done condition:** 搜索参数在 URL 中可见；刷新后状态保留；Clear filters 触发搜索；分页 page 在 URL 中；`tsc --noEmit` 通过。Artifact: `gemini-build-T04.md`.

---

## T05 — Gemini：认证前端行为 + Admin 表单校验

- **owner:** gemini
- **type:** build
- **depends_on:** T04

**Scope:**
- `frontend/components/features/properties/NavBar.tsx`
  - `signOut` 成功后调用 `router.refresh()`，防止缓存的受保护内容仍显示
- `frontend/components/features/auth/LoginForm.tsx`
  - 登录成功后读取 URL 中的 `redirectTo` 参数（由 T02 的 middleware 写入），有则跳回原页面，无则跳至 `/properties`
- `frontend/app/(dashboard)/admin/properties/page.tsx`
  - 删除房产确认改为内联 UI（如 inline confirm state 或 modal），移除原生 `window.confirm` / `window.alert`
- `frontend/components/features/admin/property-form.tsx`
  - `bedrooms` 和 `bathrooms` 字段最小值约束为 1（前端校验 + input `min` 属性）
  - 表单提交失败后，将页面滚动到第一个错误字段

**Done condition:** signOut 后 `router.refresh()` 已调用；LoginForm 登录后读取 `redirectTo` 并跳回原页面；Admin 删除无原生 `confirm`/`alert`；PropertyForm 字段最小值为 1；提交失败后滚动到错误位置；`tsc --noEmit` 通过。Artifact: `gemini-build-T05.md`.

---

## T06 — Gemini：图片降级 + 全页面状态覆盖

- **owner:** gemini
- **type:** build
- **depends_on:** T05

**Scope:**
- `frontend/components/features/properties/PropertyCard.tsx`
  - `<img>` 增加 `onError` handler，降级到 placeholder src
- `frontend/components/features/properties/PropertyDetail.tsx`
  - 同上
- 以下页面补充或修正 loading skeleton / empty state / error state（每页需含重试入口）：
  - `frontend/app/(dashboard)/properties/page.tsx`
  - `frontend/app/(dashboard)/search/page.tsx`
  - `frontend/app/(dashboard)/favorites/page.tsx`
  - `frontend/app/(dashboard)/admin/properties/page.tsx`
- 确认四页 loading/empty/error 视觉风格一致（同一骨架 class 模式、同一空态结构、同一错误提示结构）

**Done condition:** 图片 `onError` 降级已实现；四页 loading/empty/error state 均已覆盖且含重试入口；`tsc --noEmit` 通过。Artifact: `gemini-build-T06.md`.

---

## T07 — Codex review

- **owner:** codex
- **type:** review
- **depends_on:** T02, T03, T04, T05, T06

**Scope:**
- 按 `acceptance.md` 第二阶段 A 系列（A1–A16）逐条核查代码实现
- 检查 ownership boundaries（Codex 文件未被 Gemini 修改；反之亦然）
- 检查无 `fetch()` 直调、无 Supabase 越界 import、无新 npm 依赖
- 写 `review.md`（verdict: PASS / FAIL，逐条结论，失败项附 fix 建议）

**Done condition:** `review.md` 已写入，含 verdict + 所有验收条目结论 + 足够失败细节供 Claude 选择 fix_path.

---

## T08 — Claude acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T07

**Scope:**
- 读 `review.md`
- 写 `final-report.md`，disposition 单行：`## Disposition: ACCEPTED` 或 `## Disposition: FAILED`
- 更新 `status.json` feature status 为 `done` 或 `failed`

**Done condition:** `final-report.md` 已写入；`status.json` 已更新。
