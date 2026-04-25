# F1 — Authentication & Roles

## Goal

Implement end-to-end authentication using Supabase Auth, and establish a role system
(user / admin) that gates access to protected routes and admin-only functionality.

## Scope

### Backend
- Supabase JWT verification middleware (`app/core/security.py`)
- `get_current_user` dependency that extracts and validates the JWT from the
  `Authorization: Bearer <token>` header
- `require_role(role)` dependency factory for role-gated endpoints
- `GET /api/v1/auth/me` — returns the authenticated user's profile (id, email, role)
- User role stored as a custom claim in the Supabase JWT (`app_role: "user" | "admin"`)
  — set via a Supabase database function / trigger on `auth.users`
- Pydantic schemas: `UserRead` (id, email, role)
- Type published to `frontend/types/auth.ts`

### Frontend
- `lib/auth/supabase.ts` — Supabase client singleton (uses `NEXT_PUBLIC_SUPABASE_URL`
  and `NEXT_PUBLIC_SUPABASE_ANON_KEY`)
- `lib/auth/session.ts` — helpers: `getSession()`, `getAccessToken()`, `signOut()`
- `lib/api/auth.ts` — typed fetch wrapper for `GET /api/v1/auth/me`
- Auth route group `app/(auth)/`:
  - `login/page.tsx` — email + password login form (Supabase `signInWithPassword`)
  - `register/page.tsx` — email + password registration form (Supabase `signUp`)
- `components/features/auth/` — `LoginForm`, `RegisterForm` components
- Middleware `middleware.ts` at repo root — redirects unauthenticated users away from
  protected routes; redirects authenticated users away from `/login` and `/register`
- Admin guard: `app/admin/` pages require `app_role === "admin"`; redirect otherwise

### Shared
- `frontend/types/auth.ts` — `UserRead`, `AppRole` types (mirrored from backend schema)

## Non-Goals

- OAuth / social login (deferred to a later feature)
- Password reset / email verification flows (deferred)
- User management UI (deferred to admin feature)
- Any application feature beyond auth and role gating

## Constraints

- Frontend never calls Supabase directly from pages or components — only through
  `lib/auth/` helpers and `lib/api/` wrappers
- Backend validates every protected request via the `get_current_user` dependency —
  no route may bypass it
- Role is sourced from the JWT claim only — no separate DB lookup per request
- No hardcoded credentials or URLs in source; all config via env vars
- `status.json` is written only by Claude

## Dependencies

- F0 must be `done` before F1 begins (backend skeleton + frontend skeleton required)

## Required Env Vars

### Backend additions
- `SUPABASE_JWT_SECRET` — used to verify Supabase JWTs offline

### Frontend additions
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
