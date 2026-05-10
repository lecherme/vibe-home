# Frontend UX Polish

## Goal

通过先做全面只读盘点、再针对性修复，系统性解决前端存在的真实 bug 和明显 UX 缺口。
覆盖范围：认证跳转、收藏交互、页面状态、表单反馈、图片降级、分页/筛选、响应式、文案格式一致性。

执行分两阶段：
1. **T01 审计**（只读）：Gemini 盘点所有前端问题并按优先级分类，输出问题清单
2. **T02+ 修复**（由 Claude 在 T01 结果评审后定义）：按 P0 → P1 顺序逐任务修复

## Scope

### 阶段一：审计（T01 — 只读，无代码修改）

Gemini 审计以下所有维度，不修改任何文件，只产出问题清单：

**收藏交互与状态同步**
- `FavoriteButton` 409 处理、收藏状态初始化竞态
- 列表页/搜索页/详情页/收藏页收藏状态与后端同步情况

**登录后 session / 权限跳转**
- 未登录访问受保护页面的跳转行为
- 登录后 redirect 目标是否正确
- token 过期后的行为（是否静默失败、是否有提示）

**各页面状态覆盖**（`/properties`、`/properties/[id]`、`/search`、`/favorites`、`/admin`）
- loading state 是否存在
- empty state 是否存在及文案是否合理
- error state 是否存在、是否有重试入口

**表单交互反馈**
- 登录/注册表单：错误提示、loading 禁用、成功反馈
- Admin 新增/编辑房产表单：验证提示、提交 loading、成功/失败反馈

**图片加载/降级**
- 图片 `onError` 降级是否实现（placeholder 是否存在）
- 无图片房源的展示行为

**分页/筛选/URL 状态**
- 分页是否正常工作（如有）
- 搜索/筛选参数是否反映到 URL（browser back/refresh 是否保留状态）

**移动端/响应式**
- 各页面在小屏（375px）下布局是否合理（Tailwind 断点）
- 导航/头部/卡片等关键组件是否有明显响应式问题

**文案、日期、货币格式一致性**
- 价格展示格式是否统一
- 日期格式是否统一
- 英文/中文文案混用是否有异常

### 阶段二：修复（T02+ — 由 Claude 在 T01 评审后定义）

修复任务范围根据 T01 清单中 P0/P1 问题确定。
预期覆盖（但不限于）：
- `frontend/lib/api/favorites.ts` — Codex
- `frontend/components/features/favorites/favorite-button.tsx` — Gemini
- `frontend/app/(dashboard)/properties/[id]/page.tsx` — Gemini
- `frontend/app/(dashboard)/properties/page.tsx` — Gemini
- `frontend/app/(dashboard)/search/page.tsx` — Gemini
- `frontend/app/(dashboard)/favorites/page.tsx` — Gemini
- 其他由 T01 发现的 P0/P1 文件

## Non-Goals

- 图片存储架构调整（OSS/CDN 迁移）
- 新增后端 API 接口
- Seed 数据结构重构
- 搜索 / RAG 功能
- 前端性能优化（分页懒加载、SWR/React Query 缓存层）
- 后端日志、监控、安全加固
- P2 polish（颜色微调、动效、品牌升级）—— 除非 P0/P1 修完后有余力

## Constraints

- All implementation must follow `.ai/conventions.md` and `.ai/orchestration.md`.
- Workers must implement only their assigned task.
- `status.json` is updated only by Claude Code orchestration.
- 前端不得在 `frontend/app/` 或 `frontend/components/` 中直接调用 `fetch()`，所有 API 调用必须经 `frontend/lib/api/`。
- Supabase 相关 import 只允许出现在 `frontend/lib/auth/`。
- 不得引入新的 npm 依赖。
- T01 是只读任务：Gemini 不得修改任何源文件。

## Dependencies

- F8 (Production Hardening) — 已 `done`（commit 61d3ba9）

## Required Env Vars

无新增环境变量。

---

## Audit Outcome (T01) / Selected Fix Scope

**T01 审计完成：** 2026-05-11

### 发现汇总

| 级别 | 条数 |
|------|------|
| P0 真实 Bug | 5 |
| P1 明显 UX 缺口 | 6 |
| P2 Polish | 5 |

### 第二阶段纳入范围

**P0 全部纳入：**
- 收藏 409 未处理（`favorite-button.tsx` + `lib/api/favorites.ts`）
- 搜索参数未反映 URL（`search/page.tsx`）
- 退出登录未调用 `router.refresh()`（`NavBar.tsx`）
- Middleware 登录跳转无 redirect URL 保留（`middleware.ts`）
- PropertyForm `bedrooms`/`bathrooms` 最小值未约束（`property-form.tsx`）

**P1 高价值纳入：**
- 图片加载失败无 `onError` 降级（`PropertyCard.tsx`、`PropertyDetail.tsx`）
- 详情页收藏状态竞态窗口（`properties/[id]/page.tsx`）
- 列表页/搜索页收藏状态未同步（`properties/page.tsx`、`search/page.tsx`）
- Clear filters 不触发新搜索（`search/page.tsx`）
- Admin 删除使用原生 `confirm`/`alert`（`admin/properties/page.tsx`）

**P1 暂缓（本轮不修复）：**
- 列表页分页后退位置保留（依赖 URL 状态重构，风险较大，延后单独评估）
- 登录表单缺 Remember me / 密码显示切换（非核心 bug）

**P2 全部暂缓：** 本轮不修复；P0/P1 全部完成后另行决定。

### 第二阶段任务分配（T02–T08）

| 任务 | Owner | 方向 |
|------|-------|------|
| T02 | Codex | `lib/api/favorites.ts` FavoriteConflictError + `middleware.ts` redirect 保留 |
| T03 | Gemini | 收藏链路前端修复（FavoriteButton + 详情/列表/搜索页） |
| T04 | Gemini | 搜索/URL 状态持久化 + Clear filters 触发搜索 |
| T05 | Gemini | NavBar signOut refresh + Admin confirm/alert + PropertyForm 校验 |
| T06 | Gemini | 图片 onError 降级 + 各页面 loading/empty/error state |
| T07 | Codex | Review（对照 acceptance.md 验收所有修复） |
| T08 | Claude | Acceptance（写 final-report.md，更新 status.json） |
