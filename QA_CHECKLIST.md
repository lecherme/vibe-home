# QA Checklist

This checklist is organized by user flow. When a bug is found, record the
smallest reproduction under the relevant section before fixing it.

## Bug Report Template

- ID:
- Flow:
- Page/route:
- User role:
- Steps to reproduce:
- Actual result:
- Expected result:
- Console/network error:
- Severity: blocker / high / medium / low
- Status: open / fixed / verified

## 1. Route Protection And Entry Points

- [ ] Unauthenticated visit to `/properties` redirects to `/login?redirectTo=/properties`.
- [ ] Unauthenticated visit to `/search` redirects to `/login?redirectTo=/search`.
- [ ] Unauthenticated visit to `/favorites` redirects to `/login?redirectTo=/favorites`.
- [ ] Unauthenticated visit to `/admin/properties` redirects to `/login` or blocks access.
- [ ] Authenticated visit to `/login` redirects away from the auth page.
- [ ] Authenticated visit to `/register` redirects away from the auth page.
- [ ] Root route `/` has the intended product behavior.
- [ ] Invalid or external `redirectTo` values cannot redirect outside the app.

## 2. Authentication

- [ ] Login succeeds with a valid confirmed user.
- [ ] Login failure shows a clear error and leaves the form usable.
- [ ] Login redirects to the original protected route when `redirectTo` is present.
- [ ] Login without `redirectTo` lands on `/properties`.
- [ ] Register rejects mismatched passwords before calling Supabase.
- [ ] Register succeeds and shows the confirmation state.
- [ ] Register failure shows a clear error and leaves the form usable.
- [ ] Sign out clears the session and redirects to `/login`.
- [ ] Signed-out users cannot return to protected pages with browser back navigation.

## 3. Property Browsing

- [ ] `/properties` loads the first page of properties.
- [ ] Loading skeleton appears while the list request is pending.
- [ ] Empty state appears when there are no properties.
- [ ] API error state appears when the list request fails.
- [ ] Retry reloads the property list after an error.
- [ ] Pagination updates the `page` query param.
- [ ] Previous button is disabled on page 1.
- [ ] Next button is disabled on the last page.
- [ ] Property cards show image, title, price, location, bedrooms, bathrooms, and area.
- [ ] Broken property image URLs fall back to the placeholder image.
- [ ] Clicking a card opens `/properties/[id]`.

## 4. Property Detail

- [ ] Detail page loads a valid property by id.
- [ ] Loading skeleton appears while detail data is pending.
- [ ] Unknown property id renders the intended not-found behavior.
- [ ] API error state appears for non-404 request failures.
- [ ] Detail page displays the expected property fields and images.
- [ ] Favorite button initial state matches the server state.
- [ ] Favorite loading state does not shift or block the main detail layout.

## 5. Search And Filters

- [ ] `/search` loads results with no filters.
- [ ] Location search updates the URL and result list.
- [ ] Minimum price filter updates the URL and result list.
- [ ] Maximum price filter updates the URL and result list.
- [ ] Bedroom filter updates the URL and result list.
- [ ] Status filter updates the URL and result list.
- [ ] Combining filters returns consistent results.
- [ ] Clearing filters resets the URL and result list.
- [ ] Search empty state appears when no properties match.
- [ ] Search error state appears when the request fails.
- [ ] Retry reloads the same query after an error.
- [ ] Search pagination preserves active filters.
- [ ] Browser back/forward keeps form state and results in sync with the URL.

## 6. Favorites

- [ ] User can add a favorite from the property list.
- [ ] User can remove a favorite from the property list.
- [ ] User can add a favorite from the property detail page.
- [ ] User can remove a favorite from the property detail page.
- [ ] Duplicate favorite creation does not break the UI.
- [ ] Failed favorite add/remove rolls the UI back to the previous state.
- [ ] `/favorites` lists the user's saved properties.
- [ ] Empty favorites state links back to `/properties`.
- [ ] Removing a favorite from `/favorites` removes the card from the page.
- [ ] Favorites are scoped to the signed-in user.
- [ ] Admin users are blocked from favorite endpoints as intended. *(API-level check — use a request tool with an admin JWT; the UI does not hide the favorite button for admin users.)*

## 7. Admin Access Control

- [ ] Non-admin user cannot access `/admin/properties`.
- [ ] Non-admin user cannot call admin create/update/delete APIs.
- [ ] Admin user can access `/admin/properties`.
- [ ] Admin route protection is based on the expected JWT role claim.
- [ ] Admin role changes are reflected after session refresh or re-login.

## 8. Admin Property Management

- [ ] Admin property list loads existing properties.
- [ ] Admin list shows loading, empty, and error states.
- [ ] Admin can open the new property form.
- [ ] Required field validation works before create submission.
- [ ] Admin can create a valid property and return to the list.
- [ ] Created property appears in the public property list.
- [ ] Admin can open the edit form for an existing property.
- [ ] Edit form is prefilled with the current property data.
- [ ] Admin can save edits and return to the list.
- [ ] Edited property changes appear on public list and detail pages.
- [ ] Admin can cancel delete confirmation without changing data.
- [ ] Admin can delete a property after confirmation.
- [ ] Delete failure restores the row in the admin table.
- [ ] Deleted property no longer appears in public list/search/favorites.

## 9. Backend API Contracts

- [ ] `GET /api/v1/auth/me` returns the current user for a valid token.
- [ ] Protected endpoints reject missing tokens with 401.
- [ ] Protected endpoints reject invalid tokens with 401.
- [ ] Property list respects `page` and `page_size`.
- [ ] Property list caps oversized `page_size` values.
- [ ] Search validates negative numeric filters.
- [ ] Favorite endpoints reject admin users with 403.
- [ ] Admin endpoints reject non-admin users with 403.
- [ ] Admin create/update/delete return the expected status codes.
- [ ] CORS allows the configured frontend origin.
- [ ] Auth rate limit returns 429 after the configured threshold (applies to `/api/v1/auth/*` endpoints only; implemented via `AuthRateLimiter` in `auth/router.py`).
- [ ] Responses include `X-Request-ID`.

## 10. Visual And Responsive Checks

- [ ] Auth pages are usable on mobile width.
- [ ] Property grid works on mobile, tablet, and desktop widths.
- [ ] Search filters do not overflow on mobile.
- [ ] Favorite buttons do not overlap important card/detail content.
- [ ] Admin table remains usable on narrow screens.
- [ ] Buttons and form labels remain readable in loading/disabled states.
- [ ] Error and empty states do not obscure navigation.
- [ ] Placeholder images render correctly.

## 11. Regression Smoke Test

- [ ] Start backend successfully.
- [ ] Start frontend successfully.
- [ ] Login as regular user.
- [ ] Browse properties.
- [ ] Search with at least two filters.
- [ ] Open a property detail page.
- [ ] Add and remove a favorite.
- [ ] Open favorites page.
- [ ] Sign out.
- [ ] Login as admin.
- [ ] Create a property.
- [ ] Edit that property.
- [ ] Delete that property.
- [ ] Sign out.

## 12. Password Reset

> **Known issue:** Password reset links are currently broken (link opens to an error). These items are listed for future verification once the issue is resolved.

- [ ] *(blocked)* "Forgot password" link is visible on the login page.
- [ ] *(blocked)* Submitting the reset request sends a confirmation message to the user.
- [ ] *(blocked)* Clicking the reset link in the email opens the reset form.
- [ ] *(blocked)* Submitting a new password logs the user in or redirects to login.
- [ ] *(blocked)* An expired or malformed reset link shows a clear error.

## 13. Security Checks

- [ ] Submitting the login form does not put `email` or `password` in the URL query string.
- [ ] Login credentials do not appear in browser history (URL bar) after a failed or successful login.
- [ ] Login credentials do not appear in Docker / server logs at any log level.
- [ ] Network tab shows login credentials sent in the POST request body, not as URL parameters.
- [ ] `redirectTo` cannot redirect to an external origin (e.g. `//evil.com`, `https://evil.com`).
- [ ] Supabase auth tokens are not exposed in frontend logs or error messages.

