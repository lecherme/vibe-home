# F32 Acceptance Criteria

Codex review must verify each criterion. Mark PASS / FAIL with notes.

---

## Infrastructure (T01)

**A1** — `e2e/playwright.config.ts` exists and sets `workers: 1`, chromium browser, and `baseURL` from env.

**A2** — `e2e/.env.example` documents all five required env vars: `PLAYWRIGHT_BASE_URL`, `TEST_USER_EMAIL`, `TEST_USER_PASSWORD`, `TEST_ADMIN_EMAIL`, `TEST_ADMIN_PASSWORD`.

**A3** — `e2e/.gitignore` prevents `.auth/`, `test-results/`, and `.env` from being committed.

**A4** — `fixtures/auth.ts` exports `userPage`, `adminPage`, and `guestPage` fixtures. Auth is loaded from storage state files, not re-login via form in each test.

---

## Auth tests (T02 — auth.spec.ts)

**A5** — Unauthenticated visit to `/properties` and `/favorites` each assert a redirect to a URL containing `/login`.

**A6** — Login with wrong password asserts an error message is visible and the login form is still present.

**A7** — After logout, the test asserts the user is on `/login` or a public page, not a protected route.

**A8** — After authenticated visit to `/login`, the test asserts the user was redirected away (URL does not stay at `/login`).

**A9** — Register test asserts all form fields are visible and that submitting with mismatched passwords stays on `/register` without creating a Supabase account. No actual account creation occurs in the test suite.

**A10** — Security test asserts `page.url()` after login form submit does not contain `email=` or `password=`.

---

## Property tests (T02 — properties.spec.ts)

**A11** — Test asserts at least one property card is visible on `/properties`.

**A12** — Test asserts a card contains title, price, and location text.

**A13** — After clicking a card, the URL matches `/properties/` followed by an ID segment.

---

## Search tests (T02 — search.spec.ts)

**A14** — AI Search SSE chain test: all five state indicators (parsing, searching, results, summarizing, summary) are asserted via `expect(locator).toBeVisible()` or equivalent — not just `isVisible()` booleans.

**A15** — AI Search SSE test asserts no console errors occur during the streaming chain (attach a `page.on('console', ...)` listener or `page.on('pageerror', ...)`).

**A16** — Filter test asserts URL query params change after applying price or location filters.

---

## Favorites tests (T02 — favorites.spec.ts)

**A17** — Favorite toggle test asserts the toggle's state changes (aria, class, or text) after click — not just that a click happened.

**A18** — `/favorites` page load test asserts the page renders (even if empty state).

---

## Admin tests (T02 — admin.spec.ts)

**A19** — Non-admin access test asserts the admin property table is NOT present (not just that a redirect happened).

**A20** — Admin CRUD tests each assert a visible outcome: new title in list after create; updated title visible after edit; row absent after delete. All three operations target the same test-created property (identified by its unique timestamped title) — no pre-existing data is edited or deleted.

---

## Stabilization (T03)

**A21** — The build artifact for T03 includes a `## Verification` section with the actual pass/fail counts from the final test run.

**A22** — No test file uses `page.waitForTimeout()` with a value > 500 ms as a stability workaround.

**A23** — No assertion targets an empty string or a trivially-always-true condition.

---

## General

**A24** — All test files import from `../fixtures/auth` — no test duplicates the login-via-form logic for auth.

**A25** — Test selectors prefer `getByRole`, `getByLabel`, `getByTestId`, or `getByText` over raw CSS selectors where possible.
