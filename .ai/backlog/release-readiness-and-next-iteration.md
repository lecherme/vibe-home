# Release Readiness & Next Iteration

**Last updated:** 2026-06-06

This file tracks two categories:
1. **Release checklist** — items that cannot be resolved purely with code, required before going live
2. **Next iteration** — features and polish planned for a future batch

Actionable fix items remain tracked in `open-bugs.md`.

---

## Release Checklist (must complete before go-live)

- [x] **Supabase Auth 自定义 SMTP 配置** ✓ 2026-05-29
  Configured with Google SMTP (temporary). Verified: registration and password reset emails send successfully. TODO: switch to Resend or domain-based SMTP once production domain is ready.

- [x] **Supabase redirect URLs 检查** ✓ 2026-06-02
  Added production domain to Supabase Dashboard → Auth → URL Configuration. Registration email confirm and password reset verified working on production.

- [x] **`NEXT_PUBLIC_API_URL` 生产环境配置检查** ✓ 2026-06-02
  Set to `https://api.lecherme.cn` in Vercel environment variables. All API calls working in production.

- [x] **`/` 根路由和 `/health` 路由验收** ✓ 2026-06-02
  Production smoke test PASS (2026-06-02): admin login, property list/pagination/jump-page, add/edit property, /properties, search with all filters, favorites, detail page, page refresh login state, / root redirect all verified. https://api.lecherme.cn/health shows backend status. Blocked: registration email confirm and password reset (pending Supabase redirect URL config).

- [x] **清理测试房源数据** ✓ 2026-05-31
  Deleted 3 test properties (test delete / Test multi-image url). Fixed title of prop-hk-016 (removed "test edit Title" suffix). 38 properties remain, no test keywords.

- [x] **图片外链稳定性检查** ✓ 2026-05-31
  Audited all 73 image URLs (38 properties). Found 1 broken URL (`https://baidu.com/image/6` on prop-hk-016) — replaced with `https://picsum.photos/seed/hk16b/800/600`. baidu.com count now 0. Remaining distribution: 65 picsum.photos (临时 demo 来源，可用，长期由图片上传 feature 替换), 8 Supabase Storage (stable, self-hosted).

---

## Next Iteration

- [x] **图片上传 feature** ✓ 2026-06-03
  Completed as F10. Backend `POST /api/v1/admin/uploads/property-image` (admin-gated, multipart, Supabase Storage). Frontend: Upload button + hidden file input + in-flight state in `property-form.tsx`. ACCEPTED.

- [x] **shadcn/ui + Zod/form refactor** ✓ 2026-06-06
  Completed as F11–F14. property-form (F11), auth forms (F12), search/filter (F13), PaginationControls/NavBar (F14). All ACCEPTED.

- [ ] **全站 UI 统一美化**
  Consistent spacing, typography, colour tokens, and mobile responsiveness across all pages. Lower priority — display components (PropertyCard, PropertyDetail) audited in F14 planning; no interactive primitives remain. Scope TBD.

- [x] **OBS-009 — Search error stale-results UX** ✓ 2026-06-01
  On error, `setResult(null)` clears stale results immediately. Error state is now consistent whether the error occurs in-session or after navigating back. Chose Option A (clear) over Option B (keep + label) because B would still be inconsistent after navigation without persistence. 手动复测 PASS — 后端断开后旧列表消失，只显示 error banner；Retry 后端恢复后结果正常。

- [x] **OBS-010 — Search overlapping request guard** ✓ 2026-06-01
  Added `searchIdRef` counter in `performSearch` (`search/page.tsx`). Each call increments the ref; responses from superseded requests are discarded before any state setter runs. tsc PASS; 手动回归 PASS — 搜索/筛选/分页/Clear Filters/收藏状态/error retry 均正常。Race condition 本身无法通过普通 UI 直接触发（loading 期间输入锁住）。

---

这些事项不代表当前 bugfix 全部阻塞；Release Checklist 是上线前/本批次收口项，Next Iteration 是后续迭代。
