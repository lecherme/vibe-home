# Search & Filtering — Acceptance Criteria

T05 (Codex review) verifies every criterion below and writes `review.md`.
T06 (Claude acceptance) reads `review.md` and writes `final-report.md`.

---

## Criteria

| # | Criterion | Check |
|---|-----------|-------|
| A1 | Backend search service implements filter logic for location, price range, bedrooms, and status | Backend code review |
| A2 | Location filter uses case-insensitive substring match on address or city | Backend code review + test |
| A3 | Price range filter is inclusive (min_price <= price <= max_price) | Backend code review + test |
| A4 | Bedrooms filter uses >= comparison (bedrooms >= filter value) | Backend code review + test |
| A5 | Status filter uses exact match | Backend code review + test |
| A6 | Empty filter set returns all properties with pagination | Backend test |
| A7 | Invalid filter values return 422 (negative price, invalid status, etc.) | Backend test |
| A8 | Page size is capped at 100 | Backend code review + test |
| A9 | SearchFilters and SearchResult Pydantic schemas exist in backend/app/schemas/search.py | File exists check |
| A10 | GET /api/v1/properties/search endpoint exists in properties router | File exists + endpoint check |
| A11 | Frontend SearchFilters and SearchResult interfaces exist in frontend/types/search.ts | File exists check |
| A12 | searchProperties() function exists in frontend/lib/api/properties.ts with correct signature | File exists + type check |
| A13 | Frontend search page exists at frontend/app/(dashboard)/search/page.tsx | File exists check |
| A14 | Search bar and filter panel components exist in components/features/search/ | File exists check |
| A15 | Frontend uses lib/api/properties.searchProperties() for API calls, not direct fetch | Frontend code review |
| A16 | Frontend displays loading state while API call is in progress | Frontend code review |
| A17 | Frontend displays error state when API call fails | Frontend code review |
| A18 | Frontend has pagination controls (prev/next, page indicator) | Frontend code review |
| A19 | No Supabase imports in frontend search components | Frontend code review |
| A20 | No property_type filtering implementation anywhere (deferred) | Codebase search check |
| A21 | All backend tests in test_search.py pass | Test execution |
| A22 | Frontend TypeScript compiles without errors | Build check |

## Review and Acceptance

If review verdict is FAIL, Claude does NOT proceed directly to T06 acceptance.
Claude must:
1. Write `last_review_failure` to `status.json` with fix_path, failed_criteria, and fix_instructions.
2. Choose fix_path: task_retry, direct_fixup, or review_rerun.
3. Apply the fix and re-run review before acceptance.

## Rejection Conditions

- Any task modifies files outside its ownership boundary.
- Any worker modifies `status.json`.
- Any required artifact is missing or malformed.
- Property type filtering was implemented (A20 failed).
