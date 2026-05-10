# Gemini Build Report

## Task Completed
- T01

## P0 — 真实 Bug（功能不正确或产生报错）
| # | 页面/组件 | 问题描述 | 受影响文件 |
|---|-----------|----------|------------|
| 1 | `SearchPage` | 搜索/筛选参数未反映在 URL 中，导致页面刷新、浏览器后退或分享链接时状态丢失。 | `frontend/app/(dashboard)/search/page.tsx` |
| 2 | `FavoriteButton` | 虽然有乐观更新，但未处理 409（重复收藏）等后端逻辑冲突。在列表页快速点击可能导致本地状态与服务端不一致。 | `frontend/components/features/favorites/favorite-button.tsx` |
| 3 | `PropertyForm` | `validate` 函数允许 `bedrooms` 和 `bathrooms` 为 0，且没有前端字符长度限制。提交失败时没有滚动到错误位置。 | `frontend/components/features/admin/property-form.tsx` |
| 4 | `NavBar` | 退出登录仅在客户端 `router.push("/login")`，未调用 `router.refresh()`，可能导致缓存的受保护内容仍显示。 | `frontend/components/features/properties/NavBar.tsx` |
| 5 | `Middleware` | 认证跳转仅清除 `search` 参数，若用户从 `/properties?id=123` 跳转到登录，登录后无法回到原页面。 | `frontend/middleware.ts` |

## P1 — 明显 UX 缺口（功能缺失但不报错）
| # | 页面/组件 | 问题描述 | 受影响文件 |
|---|-----------|----------|------------|
| 1 | `PropertyCard`/`Detail` | 图片加载失败时未实现 `onError` 降级逻辑（尽管有 placeholder 变量但未使用 `img` 的 `onError`）。 | `frontend/components/features/properties/PropertyCard.tsx`, `PropertyDetail.tsx` |
| 2 | `PropertyDetailPage` | `isFavorite` 状态是在 `Property` 数据加载后独立异步获取的，导致页面加载瞬间收藏按钮状态闪烁（从未收藏变已收藏）。 | `frontend/app/(dashboard)/properties/[id]/page.tsx` |
| 3 | `PropertiesPage` | 列表页进入详情页后点击浏览器后退，无法保留之前的分页位置（虽有 URL 参数但初始化逻辑可能存在竞态）。 | `frontend/app/(dashboard)/properties/page.tsx` |
| 4 | `SearchPage` | 搜索结果为空时，"Clear all filters" 按钮仅重置本地 state，未触发新的搜索请求，用户需手动再次点击 Search。 | `frontend/app/(dashboard)/search/page.tsx` |
| 5 | `AdminProperties` | 删除房产使用原生 `confirm()` 和 `alert()`，与系统 UI 风格不统一且阻塞线程。 | `frontend/app/(dashboard)/admin/properties/page.tsx` |
| 6 | `LoginForm` | 缺少 "Remember me" 选项，且密码框缺少“显示/隐藏密码”切换功能。 | `frontend/components/features/auth/LoginForm.tsx` |

## P2 — Polish（体验细节，不影响主流程）
| # | 页面/组件 | 问题描述 | 受影响文件 |
|---|-----------|----------|------------|
| 1 | `PropertyCard` | 价格展示未处理货币符号国际化（硬编码 `$`）。 | `frontend/components/features/properties/PropertyCard.tsx` |
| 2 | `PropertyListSkeleton` | 骨架屏固定为 6 个，无论实际数据量或屏幕大小，导致加载完成后页面抖动。 | `frontend/components/features/properties/PropertyListSkeleton.tsx` |
| 3 | `PropertyDetail` | 日期展示使用 `toLocaleDateString()`，在不同浏览器/语言环境下格式不统一（如 MM/DD/YYYY vs YYYY/MM/DD）。 | `frontend/components/features/properties/PropertyDetail.tsx` |
| 4 | `Admin/NewProperty` | 缺少面包屑导航，仅有 "Back to list" 按钮。 | `frontend/app/(dashboard)/admin/properties/new/page.tsx` |
| 5 | `All Pages` | 移动端（375px）下，部分表格和长列表标题可能出现截断或换行不美观。 | `frontend/app/(dashboard)/**` |

## Verification
- No source files were modified during this audit.
- Files inspected: 
    - `frontend/middleware.ts`
    - `frontend/app/(dashboard)/properties/page.tsx`
    - `frontend/app/(dashboard)/properties/[id]/page.tsx`
    - `frontend/app/(dashboard)/search/page.tsx`
    - `frontend/app/(dashboard)/favorites/page.tsx`
    - `frontend/app/(dashboard)/admin/properties/page.tsx`
    - `frontend/app/(dashboard)/admin/properties/new/page.tsx`
    - `frontend/app/(dashboard)/admin/properties/[id]/edit/page.tsx`
    - `frontend/components/features/favorites/favorite-button.tsx`
    - `frontend/components/features/properties/PropertyCard.tsx`
    - `frontend/components/features/properties/PropertyDetail.tsx`
    - `frontend/components/features/properties/NavBar.tsx`
    - `frontend/components/features/auth/LoginForm.tsx`
    - `frontend/components/features/auth/RegisterForm.tsx`
    - `frontend/components/features/admin/property-form.tsx`
    - `frontend/lib/api/*.ts`
    - `frontend/lib/auth/*.ts`

## Open Issues
- 由于环境限制，无法进行真实的移动端设备测试，仅基于 Tailwind 类名进行代码逻辑审计。
- 未审计 `frontend/components/ui/` 下的底层基础组件（如 Shadcn UI），因为项目目录中该文件夹下仅有 `.gitkeep`。
