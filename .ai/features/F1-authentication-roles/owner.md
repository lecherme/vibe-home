# F1 — Ownership Boundaries

## Codex

Codex owns all backend code and all frontend infrastructure (library and type layers).

| Path | Scope |
|------|-------|
| `backend/app/api/v1/auth/` | Auth router and endpoint |
| `backend/app/core/security.py` | JWT verification, `get_current_user`, `require_role` |
| `backend/app/schemas/auth.py` | `UserRead`, `AppRole` Pydantic schemas |
| `backend/app/core/config.py` | `SUPABASE_JWT_SECRET` config field |
| `backend/tests/test_auth.py` | Auth unit tests |
| `frontend/lib/auth/supabase.ts` | Supabase client singleton |
| `frontend/lib/auth/session.ts` | `signIn`, `signUp`, `signOut`, `getSession`, `getAccessToken` |
| `frontend/lib/api/auth.ts` | `authApi.getMe()` typed fetch wrapper |
| `frontend/middleware.ts` | Route protection and role-gating middleware |
| `frontend/types/auth.ts` | `UserRead`, `AppRole` TypeScript types |
| `backend/.env.example` | Backend env var documentation |
| `frontend/.env.example` | Frontend env var documentation |

Codex must NOT touch:
- `frontend/app/` (Gemini owns pages)
- `frontend/components/` (Gemini owns UI components)

---

## Gemini

Gemini owns all frontend UI: pages and feature components.

| Path | Scope |
|------|-------|
| `frontend/app/(auth)/login/page.tsx` | Login page — renders `<LoginForm />` |
| `frontend/app/(auth)/register/page.tsx` | Register page — renders `<RegisterForm />` |
| `frontend/app/(auth)/layout.tsx` | Centered layout for auth pages |
| `frontend/components/features/auth/LoginForm.tsx` | Login form component |
| `frontend/components/features/auth/RegisterForm.tsx` | Register form component |

Gemini must NOT touch:
- `frontend/lib/` — Codex owns all library code
- `frontend/types/` — Codex owns all type definitions
- `frontend/middleware.ts` — Codex owns middleware
- `backend/` — Codex owns all backend code
- `.ai/`, `tools/`, `status.json` — Claude owns orchestration

---

## Boundary Rules

1. UI components (`frontend/components/`) must never import from `@supabase/ssr` or `@supabase/supabase-js` directly.
2. UI components must call auth operations exclusively through helpers in `frontend/lib/auth/session.ts`.
3. Pages (`frontend/app/`) must never construct fetch calls directly — all API calls go through `frontend/lib/api/`.
4. `status.json` is written only by Claude. Any write to it by Codex or Gemini is a contract violation.
5. Report files (`codex-build-*.md`, `gemini-build-*.md`, `review.md`) are written by the wrapper script capturing stdout — workers must not create these files directly.
