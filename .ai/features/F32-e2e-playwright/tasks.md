# F32 Tasks

## T01 — Playwright infrastructure

**Owner:** codex
**Type:** build
**Depends on:** []

**Scope:**
- `e2e/package.json`
- `e2e/playwright.config.ts`
- `e2e/.env.example`
- `e2e/.gitignore`
- `e2e/fixtures/auth.ts`

**Done condition:**
- `e2e/package.json` has `@playwright/test` as a dependency, plus scripts: `test`, `test:headed`, `test:ui`
- `playwright.config.ts` sets:
  - `baseURL` from `PLAYWRIGHT_BASE_URL` env (default `http://localhost:3000`)
  - browser: chromium only
  - `workers: 1` (sequential — prevents auth session conflicts)
  - reporters: `['list', ['html', { open: 'never' }]]`
  - `testDir: './tests'`, `outputDir: './test-results'`
  - Global setup file that logs in both test accounts and saves storage state to `e2e/.auth/user.json` and `e2e/.auth/admin.json`
- `.env.example` documents: `PLAYWRIGHT_BASE_URL`, `TEST_USER_EMAIL`, `TEST_USER_PASSWORD`, `TEST_ADMIN_EMAIL`, `TEST_ADMIN_PASSWORD`
- `.gitignore` covers: `.auth/`, `test-results/`, `.env`, `node_modules/`
- `fixtures/auth.ts` exports an extended `test` with:
  - `userPage`: Page with user storage state loaded
  - `adminPage`: Page with admin storage state loaded
  - `guestPage`: plain Page (no auth)
- Global setup in `playwright.config.ts` performs sign-in via the frontend login form for each account and writes the storage state files

---

## T02 — Core E2E test files

**Owner:** codex
**Type:** build
**Depends on:** [T01]

**Scope:**
- `e2e/tests/auth.spec.ts`
- `e2e/tests/properties.spec.ts`
- `e2e/tests/search.spec.ts`
- `e2e/tests/favorites.spec.ts`
- `e2e/tests/admin.spec.ts`

**Done condition:**

### `auth.spec.ts` (uses `guestPage` and `userPage` fixtures)
- `GET /properties` without auth → URL contains `/login`
- `GET /favorites` without auth → URL contains `/login`
- Login with valid credentials → lands on `/properties` (default) or `redirectTo` target
- Login with wrong password → error text visible, login form still present
- Logout → page lands on `/login` or `/` with no session
- Authenticated user visits `/login` → redirected away (does not stay on `/login`)
- Authenticated user visits `/register` → redirected away
- Register page: form fields (email, password, confirm password, submit button) are visible
- Register page: submitting with mismatched passwords stays on `/register` and does not create an account (no actual Supabase account creation in tests)
- After login form submit, page URL does NOT contain `email=` or `password=`

### `properties.spec.ts` (uses `userPage`)
- `/properties` renders at least one property card
- Each card has visible: title text, price text, location text
- "Next" pagination button: if present and enabled, clicking it changes the list or URL
- Clicking any property card navigates to `/properties/` followed by an ID
- Detail page at `/properties/[id]` renders the property title

### `search.spec.ts` (uses `userPage`)
- `/search` page loads without error
- Typing a location value and submitting → results list or empty state renders
- Setting min price and max price and submitting → URL contains price params
- Submitting empty search → all params cleared or results reset
- **AI Search SSE chain** (triggered by a natural-language query, e.g. "two bedroom near Central"):
  - A "parsing" status indicator or text becomes visible after submit
  - A "searching" status indicator or text becomes visible
  - Result cards become visible
  - A "summarizing" status indicator or text becomes visible
  - A summary text block is visible after streaming completes
  - The entire chain completes without a JS error in the console

### `favorites.spec.ts` (uses `userPage`)
- On `/properties`, find a property card and click its favorite toggle → toggle state changes (aria-pressed, icon class, or label change)
- Click the same toggle again → state reverts
- Navigate to `/favorites` → page renders (either shows cards or an empty state)
- If a favorited property is shown: clicking remove/unfavorite on `/favorites` removes it from the list

### `admin.spec.ts` (uses `userPage` for access-denied check, `adminPage` for CRUD)

**Non-destructive data policy:** Tests must NEVER delete or permanently modify pre-existing property data.
The create → edit → delete sequence must operate on a single test-owned property created within the same test run:
1. Create a new property with a unique timestamped title (e.g. `E2E Test Property 2026-07-17T...`)
2. Edit that same newly created property
3. Delete that same newly created property

Do NOT click edit or delete on any property that was not created in step 1. Use the unique title to identify the test property throughout.

- Non-admin navigates to `/admin/properties` → blocked (HTTP 403, redirect to `/login`, or error page — check that admin table is NOT rendered)
- Admin navigates to `/admin/properties` → property management table is rendered
- Admin creates a new property with a unique timestamped title → that title appears in the list
- Admin edits the newly created property (title suffix changed), saves → updated title visible in list
- Admin deletes the newly created property, confirms → that property is no longer in the table

---

## T03 — Execution and stabilization

**Owner:** codex
**Type:** build
**Depends on:** [T02]

**Scope:**
- `e2e/tests/auth.spec.ts`
- `e2e/tests/properties.spec.ts`
- `e2e/tests/search.spec.ts`
- `e2e/tests/favorites.spec.ts`
- `e2e/tests/admin.spec.ts`
- `e2e/fixtures/auth.ts`
- `e2e/playwright.config.ts`

**Context:**
This task runs all tests against the live Docker Compose stack. Its purpose is
NOT to add new cases, but to confirm the existing suite is stable and to fix any
issues found (flaky selectors, timing, auth state, missing waitFor, wrong
assertions). The done condition describes the stable end state — not what was
changed.

**Setup required before running:**
```
cd e2e && npm install && npx playwright install chromium
```
Tests are run with:
```
npx playwright test
```

**Done condition:**
- All tests in all 5 spec files pass (exit 0) on two consecutive runs
- No test uses `page.waitForTimeout()` with a hardcoded delay > 500 ms as a stability workaround
- No test uses `textContent()` assertions that match partial unintended strings (e.g., matching `""` because the element is empty)
- The AI Search SSE chain test in `search.spec.ts` passes: all 5 state indicators (parsing, searching, results, summarizing, summary) appear in sequence without console errors
- Auth fixtures correctly load stored sessions — no test logs in via form when it should use a fixture
- The final test run output (pass count, skip count, fail count) is recorded in the build artifact under `## Verification`

---

## T04 — Codex review

**Owner:** codex
**Type:** review
**Depends on:** [T01, T02, T03]

**Artifact:** `review.md`

---

## T05 — Claude acceptance

**Owner:** claude
**Type:** acceptance
**Depends on:** [T04]
