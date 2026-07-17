# F32 — Playwright E2E Test Suite

## Goal

Set up a Playwright-based end-to-end test suite covering the core user flows of
the vibe-home app. Tests run against a locally running Docker Compose stack
(frontend on `localhost:3000`, backend on `localhost:8000`).

## Non-Goals

- CI/CD pipeline integration
- Full QA_CHECKLIST.md coverage — focus on happy path + primary error scenarios
- Visual regression / screenshot diffing
- Mocking backend or Supabase APIs — tests hit real services

## Test Scope

### Auth and Route Protection
- Unauthenticated access to protected routes → redirect to `/login`
- Login success → redirect to intended page (with `redirectTo`)
- Login failure → error shown, form stays usable
- Logout → session cleared, redirect to `/login`
- Authenticated users visiting `/login` or `/register` → redirected away
- Register page renders with all required fields visible
- Register rejects mismatched passwords client-side without creating any account
- Login form: credentials not in URL (security)

### Property Browsing
- `/properties` loads a list of properties
- Property card shows key fields (title, price, location)
- Pagination (next/prev button behavior)
- Clicking a card navigates to `/properties/[id]`
- Detail page loads and shows property title and fields

### AI Search (SSE streaming chain)
- Typing a query and submitting triggers streaming mode
- Progress states appear in order: **parsing** → **searching** → **results** → **summarizing** → **summary**
- Final summary text is visible after streaming completes
- Non-AI filter combination (location + price) shows results
- Clearing filters resets results
- Empty state appears when no match

### Favorites
- Add favorite from property list (icon/button state changes)
- Remove favorite from property list (state reverts)
- `/favorites` page shows saved properties
- Removing from favorites page removes the card

### Admin
- Non-admin user navigating to `/admin/properties` is blocked (redirect or 403)
- Admin user can access `/admin/properties`
- Admin can create a new property
- Admin can edit an existing property
- Admin can delete a property

## Environment

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Auth: fixed test accounts via `e2e/.env` (pre-created in Supabase)
  - Regular user: `TEST_USER_EMAIL` / `TEST_USER_PASSWORD`
  - Admin user: `TEST_ADMIN_EMAIL` / `TEST_ADMIN_PASSWORD` (needs `app_role=admin` in Supabase `app_metadata`)

## Output Location

```
e2e/
├── package.json
├── playwright.config.ts
├── .env.example
├── .gitignore
├── fixtures/
│   └── auth.ts
└── tests/
    ├── auth.spec.ts
    ├── properties.spec.ts
    ├── search.spec.ts
    ├── favorites.spec.ts
    └── admin.spec.ts
```

## Dependencies

- F0–F31 all done (app is feature-complete)
