# Review

## Verdict
PASS

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | `backend/app/schemas/search.py:7-15` defines `bedrooms_min/max` and `bathrooms_min/max`; old `bedrooms`/`bathrooms` filter fields are gone. |
| A2 | PASS | `backend/app/services/search/service.py:32-53` applies `< bedrooms_min`, `> bedrooms_max`, `< bathrooms_min`, `> bathrooms_max` skip logic. |
| A3 | PASS | `backend/app/services/ai_search/service.py:48-141` implements deterministic price-unit expansion, min/max price extraction, and comparator-based bedroom/bathroom bounds including `+1` / `-1` cases. |
| A4 | PASS | `_parse_filters()` calls `_normalize_query()` first at `backend/app/services/ai_search/service.py:179-191` and only sends unresolved text to the LLM. |
| A5 | PASS | The prompt at `backend/app/services/ai_search/service.py:193-200` asks only for `location`, `status`, and `remainder`, and explicitly forbids re-inferring price/bed/bath fields. |
| A6 | PASS | `backend/tests/eval_set.json` contains 30 queries; `backend/tests/test_eval.py:14-45` enforces `>=25` and `>=80%`; activity log/build artifact records in-container eval pass at `30/30`. |
| A7 | PASS | The regular search endpoint was updated in the repo’s equivalent file, `backend/app/api/v1/properties/router.py:47-72`, with `bedrooms_min/max` and `bathrooms_min/max`. |
| A8 | PASS | Activity log/build artifact records `import app.main` passing in the backend container; local rerun was not possible in this shell because backend deps are not installed. |
| A9 | PASS | `frontend/types/search.ts:3-11` publishes the updated `SearchFilters` shape to `frontend/types/`. |
| A10 | PASS | `frontend/components/features/search/ai-parsed-filters-card.tsx:42-66` renders `>= X Beds`, `<= X Beds`, and `X–Y Beds`, with the same logic for bathrooms. |
| A11 | PASS | `frontend/lib/api/properties.ts:84-125` and `frontend/app/(dashboard)/search/page.tsx:32-39, 93-121` use the renamed min/max query params consistently. |
| A12 | PASS | `npx tsc --noEmit` exited `0` in this review run. |
| A13 | PASS | Code path supports `"2个卧室以上 预算2000万"`: `_normalize_query()` yields `bedrooms_min=2` and `max_price=20000000`, and the card renders `>= 2 Beds` plus `< $20000000`. |
| A14 | PASS | Code path supports `"more than 2 bedrooms under 8000000 hkd"`: `_normalize_query()` yields `bedrooms_min=3` and `max_price=8000000`, and the card renders `>= 3 Beds` plus `< $8000000`. |
| A15 | PASS | Code path supports `"less than 4 bedrooms"`: `_normalize_query()` maps this to `bedrooms_max=3`, and the card renders `<= 3 Beds`. |
| A16 | PASS | Filter-search wiring remains aligned end-to-end: shared `SearchFilters`, updated URL parsing/serialization, updated API client, and successful typecheck. |

## Issues Found
- MINOR: There is no automated frontend test covering `AiParsedFiltersCard` chip rendering or the updated filter URL/query-param flow; frontend verification is currently typecheck-only.

## Required Fixes
- None.

## Approved Items
- Deterministic parsing remains in the backend; no query-parsing business logic was moved into frontend components.
- `status.json` is modified in the worktree, but the authoritative activity log attributes those workflow edits to `claude`; I found no evidence of Codex or Gemini modifying it.
- The current rerun reason is resolved: `frontend/components/features/search/ai-parsed-filters-card.tsx` no longer collapses equal min/max values to a single chip label.
