# Frontend UX Polish — Acceptance Criteria

本文件随 feature 演进追加，不整体重写。
当前定义第一阶段（T01 审计）的验收条件；第二阶段验收项将在 T01 完成后追加。

---

## 第一阶段：T01 审计验收

T01 由 Claude 人工评审（不经 Codex review 脚本）。

### 审计产出验收

| # | 验收点 | 检查方式 |
|---|--------|----------|
| AU-1 | `gemini-build-T01.md` 已存在且非空 | 文件存在性检查 |
| AU-2 | 含 P0 / P1 / P2 三个分类章节 | 检查章节标题 |
| AU-3 | 每条问题含：页面/组件名称、问题描述、受影响文件路径 | 抽查若干条目 |
| AU-4 | 已覆盖全部 8 个审计维度（收藏、session、页面状态、表单、图片、分页/URL、响应式、文案格式） | 对照 tasks.md 审计范围逐维度确认 |
| AU-5 | T01 期间无任何前端/后端源文件被修改；T01 只允许新增或更新 `gemini-build-T01.md` 这一审计产物，`status.json` 等编排文件仍仅由 Claude 按流程维护 | `git diff HEAD -- frontend/ backend/` 无任何差异 |

### T01 完成后 Claude 的决策输出

Claude 评审 T01 清单后，在 `status.json` 的 `activity_log` 中记录以下决策：
- F9 scope 是否扩展（列出新增受影响文件）
- 是否拆分为两个 feature（F9a / F9b）
- 第二阶段任务拆分方案（T02 起始方向）

---

---

## 第二阶段：T02–T06 修复验收（T07 Codex review 逐条核查）

### 一、交互正确性（Interaction Correctness）

| # | 验收点 | 核查方式 |
|---|--------|----------|
| A1 | `FavoriteConflictError` 已从 `lib/api/favorites.ts` 导出 | `grep -n "FavoriteConflictError"` in favorites.ts |
| A2 | `addFavorite` 在 409 时抛出 `FavoriteConflictError`，非 409 仍抛泛型 `Error` | grep 409 分支 + catch 路径 |
| A3 | `FavoriteButton` catch 中捕获 `FavoriteConflictError` 时 `isFavorited` 置为 `true`，不调用 revert | grep `FavoriteConflictError` in favorite-button.tsx，确认无 `setIsFavorited(previousState)` |
| A4 | 详情页增加 `isFavoriteLoaded` guard，`FavoriteButton` 仅在其为 `true` 后渲染 | grep `isFavoriteLoaded` in properties/[id]/page.tsx |
| A5 | 列表页/搜索页挂载后获取收藏列表并传 `isFavorited` 给 `PropertyCard` | grep 收藏 Set 构建逻辑 in properties/page.tsx + search/page.tsx |

### 二、搜索/URL 状态

| # | 验收点 | 核查方式 |
|---|--------|----------|
| A6 | 搜索/筛选参数持久化到 URL query string | grep `useSearchParams`/`useRouter` + URL write 逻辑 in search/page.tsx |
| A7 | Clear filters 后自动触发新搜索，不需手动再点 Search | grep clear filters handler，确认触发 search effect |
| A8 | 分页 page 参数持久化到 URL | grep `?page=` 或等效写入逻辑 in properties/page.tsx |

### 三、认证前端行为

| # | 验收点 | 核查方式 |
|---|--------|----------|
| A9 | Middleware 登录跳转携带 `redirectTo` 参数 | grep `redirectTo` in middleware.ts |
| A10 | `NavBar` signOut 成功后调用 `router.refresh()` | grep `router.refresh` in NavBar.tsx |

### 四、Admin 表单校验

| # | 验收点 | 核查方式 |
|---|--------|----------|
| A11 | Admin 删除确认已移除原生 `confirm`/`alert`，改为内联 UI | grep `window.confirm`/`window.alert` in admin/properties/page.tsx，确认不存在 |
| A12 | `PropertyForm` `bedrooms`/`bathrooms` 最小值约束为 1 | grep `min` 属性或校验逻辑 in property-form.tsx |

### 五、页面状态与图片降级

| # | 验收点 | 核查方式 |
|---|--------|----------|
| A13 | `PropertyCard` 和 `PropertyDetail` 图片有 `onError` 降级 handler | grep `onError` in PropertyCard.tsx + PropertyDetail.tsx |
| A14 | `/properties`、`/search`、`/favorites`、`/admin` 四页均有 loading skeleton | grep `animate-pulse` 或骨架实现 in 各 page.tsx |
| A15 | 四页均有 empty state（含文案） | grep empty state 条件渲染分支 in 各 page.tsx |
| A16 | 四页均有 error state（含重试入口） | grep error state + retry 逻辑 in 各 page.tsx |

### 六、边界与约束

| # | 核查点 |
|---|--------|
| B1 | Gemini 未修改 `frontend/lib/` 或 `frontend/middleware.ts` |
| B2 | Codex 未修改 `frontend/app/` 或 `frontend/components/` |
| B3 | `frontend/app/` 和 `frontend/components/` 中无直接 `fetch()` 调用 |
| B4 | Supabase 相关 import 仅出现在 `frontend/lib/auth/` |
| B5 | `package.json` 无新增依赖 |
| B6 | `tsc --noEmit` 编译无错误 |

## 通用拒绝条件（全阶段适用）

- 任何 worker 修改了 `status.json`
- 任何任务修改了其 ownership boundary 之外的文件
- 任何必要 artifact 缺失或格式不符
