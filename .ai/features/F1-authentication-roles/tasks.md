# F1 — Tasks

Every task has exactly one owner. Collaboration happens through sequential tasks, not shared tasks.

---

## T01 — Backend auth skeleton

- **owner:** codex
- **type:** scaffold
- **depends_on:** none
- **title:** Scaffold backend auth module structure and env config

**Scope:**
- Create `backend/app/api/v1/auth/` with empty `__init__.py` and `router.py`
- Create `backend/app/core/security.py` with stub signatures (no implementation yet):
  - `verify_jwt(token: str) -> dict`
  - `get_current_user` FastAPI dependency stub
  - `require_role(role: str)` dependency factory stub
- Add `SUPABASE_JWT_SECRET` to `backend/app/core/config.py` (loaded from env)
- Update `backend/.env.example` with `SUPABASE_JWT_SECRET=<your-jwt-secret>`
- Create `backend/app/schemas/auth.py` with `UserRead` and `AppRole` Pydantic schemas
- Write `UserRead` and `AppRole` types to `frontend/types/auth.ts`
- Register auth router in `backend/app/main.py` under `/api/v1/auth`

**Done condition:** Backend starts without errors; auth module is importable; `frontend/types/auth.ts` exists with correct types

---

## T02 — Backend JWT verification and /me endpoint

- **owner:** codex
- **type:** backend
- **depends_on:** T01
- **title:** Implement JWT middleware and GET /api/v1/auth/me

**Scope:**
- Implement `verify_jwt(token: str) -> dict` in `security.py`:
  - Decode and verify Supabase JWT using `SUPABASE_JWT_SECRET` (PyJWT)
  - Raise `HTTPException(401)` on invalid or expired token
- Implement `get_current_user` dependency:
  - Extracts `Authorization: Bearer <token>` header
  - Calls `verify_jwt`; returns `UserRead` (id, email, role from `app_role` claim)
  - Raises `HTTPException(401)` if header missing or token invalid
- Implement `require_role(role)` dependency factory:
  - Calls `get_current_user`; raises `HTTPException(403)` if role does not match
- Implement `GET /api/v1/auth/me` in `router.py`:
  - Protected by `get_current_user`
  - Returns `UserRead`
- Write unit tests in `backend/tests/test_auth.py`:
  - Valid JWT → 200 with correct user data
  - Missing header → 401
  - Invalid/expired token → 401
  - Wrong role → 403

**Done condition:** All tests pass; `GET /api/v1/auth/me` returns 200 with valid JWT and 401 without

---

## T03 — Frontend auth library

- **owner:** codex
- **type:** infra
- **depends_on:** T01
- **title:** Implement lib/auth/ helpers and lib/api/auth.ts

**Scope:**
- Create `frontend/lib/auth/supabase.ts`:
  - Supabase client singleton using `createBrowserClient` from `@supabase/ssr`
  - Uses `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- Create `frontend/lib/auth/session.ts`:
  - `signIn(email: string, password: string): Promise<void>` — calls `supabase.auth.signInWithPassword`; throws on error
  - `signUp(email: string, password: string): Promise<void>` — calls `supabase.auth.signUp`; throws on error
  - `signOut(): Promise<void>`
  - `getSession(): Promise<Session | null>`
  - `getAccessToken(): Promise<string | null>`
  - These are the ONLY allowed entry points for UI-triggered authentication — UI components must not call Supabase directly
- Create `frontend/lib/api/auth.ts`:
  - `authApi.getMe(): Promise<UserRead>` — calls `GET /api/v1/auth/me` with Bearer token
- Update `frontend/.env.example` with `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`

**Done condition:** TypeScript compiles without errors; no Supabase calls outside `lib/auth/` or `lib/api/`

---

## T04 — Next.js middleware and route protection

- **owner:** codex
- **type:** backend
- **depends_on:** T03
- **title:** Implement Next.js middleware for route protection

**Scope:**
- Create `frontend/middleware.ts`:
  - Uses `@supabase/ssr` server client to read session from cookies
  - Unauthenticated users hitting any route outside `/(auth)` are redirected to `/login`
  - Authenticated users hitting `/login` or `/register` are redirected to `/`
  - Admin routes (`/admin/*`) redirect non-admin users to `/` (check `app_role` claim)
- Middleware `matcher` config covers `/((?!_next/static|_next/image|favicon.ico).*)` 

**Done condition:** TypeScript compiles; middleware file exists with correct matcher config

---

## T05 — Auth UI components and pages

- **owner:** gemini
- **type:** ui
- **depends_on:** T03, T04
- **title:** Scaffold login and register pages with form components

**Scope:**
- Create `frontend/components/features/auth/LoginForm.tsx`:
  - Email + password fields
  - Submit calls `signIn` from `lib/auth/session.ts`; on success redirects to `/`
  - Explicit loading state: button disabled and shows loading indicator while submitting
  - Explicit error state: inline error message displayed on failure
  - No business logic — only form state and calls to auth helpers from `lib/auth/session.ts`
- Create `frontend/components/features/auth/RegisterForm.tsx`:
  - Email + password + confirm-password fields
  - Submit calls `signUp` from `lib/auth/session.ts`; on success shows "check your email" message
  - Explicit loading state: button disabled and shows loading indicator while submitting
  - Explicit error state: inline error message displayed on failure
  - No business logic — only form state and calls to auth helpers from `lib/auth/session.ts`
- Create `frontend/app/(auth)/login/page.tsx` — renders `<LoginForm />`
- Create `frontend/app/(auth)/register/page.tsx` — renders `<RegisterForm />`
- Create `frontend/app/(auth)/layout.tsx` — minimal centered layout for auth pages
- Basic Tailwind styling only; no custom design system yet

**Absolute constraints (contract — any violation is a blocker):**
- Do NOT import `@supabase/ssr` or `@supabase/supabase-js` anywhere in `components/` or `app/`
- Do NOT call `supabase.auth.*` directly — all auth actions must go through `lib/auth/session.ts`
- Do NOT call `fetch()` directly — all API calls must go through `lib/api/`
- Do NOT write business logic in components — only form state, loading state, error state, and calls to `lib/auth/session.ts`
- Do NOT modify `frontend/lib/`, `frontend/types/`, `frontend/middleware.ts`, or any backend file

**Done condition:** Pages render without errors; forms handle loading and error states explicitly; no direct Supabase or fetch calls in components or pages

---

## T06 — Codex review

- **owner:** codex
- **type:** review
- **depends_on:** T01, T02, T03, T04, T05
- **title:** Review F1 implementation against acceptance criteria

**Scope:**
- Validate all T01–T05 deliverables against `acceptance.md`
- Check for boundary violations (Supabase calls outside lib/auth/, business logic in components)
- Verify JWT verification is correct and tests cover all cases
- Verify middleware protects all required routes
- Write `review.md`

**Done condition:** `review.md` written with a verdict and per-criterion results

---

## T07 — Claude acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T06
- **title:** Validate F1 and write final acceptance result

**Scope:**
- Read `review.md` produced by T06
- Verify all acceptance criteria in `acceptance.md` are addressed
- Write `final-report.md` with disposition `accepted` or `failed`
- If `failed`: note specific failing criteria and return affected tasks to `pending` in `status.json`
- Update `status.json` feature status to `done` or `failed`

**Done condition:** `final-report.md` written with a clear disposition; `status.json` updated to reflect final feature state
