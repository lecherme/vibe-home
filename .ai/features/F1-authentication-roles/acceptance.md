# F1 — Acceptance Criteria

T06 (Codex review) verifies every criterion below and writes `review.md`.
T07 (Claude acceptance) reads `review.md` and writes `final-report.md` with the final disposition.

---

## Backend Skeleton (T01)

| # | Criterion | Check |
|---|-----------|-------|
| S1 | `backend/app/api/v1/auth/` exists with `__init__.py` and `router.py` | Verify files exist |
| S2 | `backend/app/core/security.py` exists with stub signatures for `verify_jwt`, `get_current_user`, `require_role` | Check file and function signatures |
| S3 | `SUPABASE_JWT_SECRET` declared in `backend/app/core/config.py` and loaded from env | Check config field; no hardcoded value |
| S4 | `backend/.env.example` includes `SUPABASE_JWT_SECRET` placeholder | Check file |
| S5 | `backend/app/schemas/auth.py` defines `UserRead` (id, email, role) and `AppRole` | Check schema fields |
| S6 | `frontend/types/auth.ts` defines `UserRead` and `AppRole` mirroring backend schemas | Check types match |
| S7 | Auth router registered in `backend/app/main.py` under `/api/v1/auth` | Check router include |
| S8 | Backend starts without import errors | `uvicorn app.main:app` exits cleanly |

## Backend JWT & /me Endpoint (T02)

| # | Criterion | Check |
|---|-----------|-------|
| J1 | `verify_jwt` decodes and verifies Supabase JWT using `SUPABASE_JWT_SECRET` | Check implementation uses PyJWT |
| J2 | `verify_jwt` raises `HTTPException(401)` on invalid or expired token | Check unit test: invalid token → 401 |
| J3 | `get_current_user` extracts `Authorization: Bearer` header and returns `UserRead` | Check implementation |
| J4 | `get_current_user` raises `HTTPException(401)` if header is missing | Check unit test: no header → 401 |
| J5 | `require_role` raises `HTTPException(403)` if authenticated user's role does not match | Check unit test: wrong role → 403 |
| J6 | `GET /api/v1/auth/me` returns 200 with `UserRead` for valid JWT | Check unit test: valid JWT → 200 |
| J7 | `GET /api/v1/auth/me` returns 401 without a valid JWT | Check unit test: no/invalid JWT → 401 |
| J8 | All unit tests in `backend/tests/test_auth.py` pass | Run test suite |

## Frontend Auth Library (T03)

| # | Criterion | Check |
|---|-----------|-------|
| L1 | `frontend/lib/auth/supabase.ts` exports a Supabase client singleton | Check file exists and exports client |
| L2 | Supabase client uses `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` — no hardcoded values | Check env var usage |
| L3 | `frontend/lib/auth/session.ts` exports `signIn`, `signUp`, `signOut`, `getSession`, `getAccessToken` | Check all five exports exist |
| L4 | `signIn` and `signUp` are the ONLY entry points for UI-triggered auth — no direct `supabase.auth.*` calls outside `frontend/lib/auth/` (verified via import and usage scan) | Grep for `supabase.auth.` outside `lib/auth/` |
| L5 | `frontend/lib/api/auth.ts` exports `authApi.getMe()` that calls `GET /api/v1/auth/me` with Bearer token | Check implementation |
| L6 | `frontend/.env.example` includes `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Check file |
| L7 | TypeScript compiles without errors across all T03 files | `tsc --noEmit` |

## Middleware & Route Protection (T04)

| # | Criterion | Check |
|---|-----------|-------|
| M1 | `frontend/middleware.ts` exists with correct `matcher` config | Check file and matcher pattern |
| M2 | Unauthenticated requests to protected routes redirect to `/login` | Check middleware logic |
| M3 | Authenticated users hitting `/login` or `/register` redirect to `/` | Check middleware logic |
| M4 | Requests to `/admin/*` from non-admin users redirect to `/` | Check `app_role` claim check in middleware |
| M5 | Middleware reads session from cookies via `@supabase/ssr` server client — no direct Supabase import in pages | Check import source |
| M6 | TypeScript compiles without errors | `tsc --noEmit` |

## Auth UI (T05)

| # | Criterion | Check |
|---|-----------|-------|
| U1 | `frontend/components/features/auth/LoginForm.tsx` exists and renders email + password fields | Check file |
| U2 | `LoginForm` calls `signIn` from `lib/auth/session.ts` — no direct Supabase import | Grep for `@supabase` in `LoginForm.tsx` — must be absent |
| U3 | `frontend/components/features/auth/RegisterForm.tsx` exists and renders email + password + confirm-password fields | Check file |
| U4 | `RegisterForm` calls `signUp` from `lib/auth/session.ts` — no direct Supabase import | Grep for `@supabase` in `RegisterForm.tsx` — must be absent |
| U5 | Both forms display inline error messages on failure | Check error state handling |
| U6 | `frontend/app/(auth)/login/page.tsx` and `register/page.tsx` exist and render their respective form components | Check files |
| U7 | `frontend/app/(auth)/layout.tsx` exists | Check file |
| U8 | No business logic in any component — only form state and calls to `lib/auth/session.ts` | Review component code |
| U9 | No direct `fetch()` usage in `app/` or `components/` — all API calls must go through `frontend/lib/api/` | Grep for `fetch(` in `app/` and `components/` |

---

## Boundary Enforcement (all tasks)

| # | Criterion | Check |
|---|-----------|-------|
| B1 | No `@supabase/ssr` or `@supabase/supabase-js` imports outside `frontend/lib/auth/` | Grep for `@supabase` outside `lib/auth/` |
| B2 | No hardcoded secrets or production URLs in source files; localhost fallback is allowed for development | Grep for hardcoded production URLs, API keys, or JWT secrets in source |
| B3 | `status.json` was not modified by Codex or Gemini | Check git diff on `status.json` |
| B4 | No report files created directly by workers | Check that `codex-build-*.md` and `gemini-build-*.md` were created by the wrapper (stdout capture), not by the worker process writing files |
| B5 | Supabase SSR usage rules enforced: middleware uses `@supabase/ssr` server client; UI components do NOT import `@supabase/ssr` or `@supabase/supabase-js` directly; Supabase browser client exists only in `frontend/lib/auth/supabase.ts`; all UI-triggered auth calls go through `frontend/lib/auth/session.ts` | Import scan across `app/`, `components/`, `middleware.ts` |

---

## Review and Acceptance (T06 + T07)

If T06 verdict is FAIL, Claude must return the failed task(s) to `pending` in `status.json` before retry.

**T06 — Codex review** runs `tools/run_codex_review.sh` and writes `review.md` containing:
- A per-criterion PASS/FAIL table covering S1–S8, J1–J8, L1–L7, M1–M6, U1–U9, B1–B5
- A list of issues found (BLOCKER / WARNING / MINOR)
- Required fixes for any blockers
- An overall verdict: PASS or FAIL

**T07 — Claude acceptance** reads `review.md` and writes `final-report.md` containing:
- Final disposition: `accepted` or `failed`
- If `failed`: the specific criteria that failed and which tasks must be retried
- Claude then updates `status.json` feature status to `done` or `failed`

---

## Rejection Conditions

Codex review (T06) must mark the verdict as **FAIL** if any of these are true:

- Any criterion above is not met
- Any component or page imports directly from `@supabase/ssr` or `@supabase/supabase-js`
- Any UI-triggered auth call bypasses `lib/auth/session.ts`
- `GET /api/v1/auth/me` is accessible without a valid JWT
- Middleware does not redirect unauthenticated users from protected routes
- Hardcoded secrets or production URLs in any source file
- `status.json` was modified by Codex or Gemini
