# Release Readiness & Next Iteration

**Last updated:** 2026-05-27

This file tracks two categories:
1. **Release checklist** — items that cannot be resolved purely with code, required before going live
2. **Next iteration** — features and polish planned for a future batch

Actionable fix items remain tracked in `open-bugs.md`.

---

## Release Checklist (must complete before go-live)

- [ ] **Supabase Auth 自定义 SMTP 配置**
  Default Supabase email service has low rate limits and poor deliverability. Configure a custom SMTP provider before real users register or reset passwords. See Supabase Dashboard → Auth → SMTP Settings.

- [ ] **Supabase redirect URLs 检查**
  Verify that all auth redirect URLs (confirm email, password reset) in Supabase Dashboard → Auth → URL Configuration match the production domain. Dev `localhost:3000` entries should not be the only entries.

- [ ] **`NEXT_PUBLIC_API_URL` 生产环境配置检查**
  Confirm the env var is set correctly in the production deployment. `frontend/lib/api/config.ts` throws on missing value — a misconfigured deployment will break all API calls at runtime.

- [ ] **`/` 根路由和 `/health` 路由验收**
  Verify on production: unauthenticated → `/login`; user role → `/properties`; admin role → `/admin/properties`; `/health` shows backend status.

- [ ] **清理测试房源数据**
  Remove or archive properties with obvious test titles (e.g. containing "test", "测试", "mock", "demo"). Check via Admin → Properties list before launch.

- [ ] **图片外链稳定性检查**
  Audit image URLs currently in the database. External URLs may become unavailable. Replace with stable hosting or document known broken images before launch. Long-term fix is the image upload feature (see Next Iteration).

---

## Next Iteration

- [ ] **图片上传 feature**
  Replace external image URL input with Supabase Storage upload: drag-and-drop or file picker, preview, delete/replace. Requires Supabase Storage bucket setup. Scope includes `property-form.tsx`, backend storage integration, and potentially Zod validation.

- [ ] **shadcn/ui + Zod/form refactor**
  Standardise UI components across the app using shadcn/ui. Migrate form validation from hand-written checks to Zod schemas. Deferred from BUG-015-FIX; natural companion to the image upload feature.

- [ ] **全站 UI 统一美化**
  Consistent spacing, typography, colour tokens, and mobile responsiveness across all pages. Scope TBD after shadcn/ui adoption.

- [ ] **OBS-009 — Search error stale-results UX**
  When a search request fails, the page retains the last successful result list under the fetch error banner. After navigating to a detail page and returning, the stale list is gone and only the error state shows. Both behaviors are functional and retry works correctly. Decide UX policy in a later polish pass: either clear stale results on error, or keep them with a "Showing last successful results" label.

---

这些事项不代表当前 bugfix 全部阻塞；Release Checklist 是上线前/本批次收口项，Next Iteration 是后续迭代。
