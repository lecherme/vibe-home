# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | Verified in backend container: `_is_property_search("一室两厅") == True`. |
| A2 | PASS | Verified in backend container: `_is_property_search("一室两厅 一家三口") == True`. |
| A3 | PASS | Verified in backend container: `_is_property_search("两房一厅") == True`. |
| A4 | PASS | Verified in backend container: `_is_property_search("三室两卫") == True`. |
| A5 | PASS | `_is_property_search()` normalizes Chinese digits before checking `_PROPERTY_SEARCH_PATTERNS`, and the room-count pattern now includes `厅`. |
| A6 | PASS | Verified in backend container: `_is_property_search("为什么房价上涨") == False`. |
| A7 | PASS | Verified in backend container: `_extract_living_rooms("一室两厅") == 2`. |
| A8 | PASS | Verified in backend container: `_extract_living_rooms("三室两厅") == 2`. |
| A9 | PASS | Verified in backend container: `_extract_living_rooms("两室一厅") == 1`. |
| A10 | PASS | Verified in backend container: `_extract_living_rooms("两室") == None`. |
| A11 | PASS | `ai_search()` emits `IntentField(field="living_rooms", value=2, filterable=False)`, and `backend/tests/test_eval_f27.py` asserts it. |
| A12 | PASS | `living_rooms` is surfaced only through `interpreted_intent`; it is not written into `SearchFilters`. |
| A13 | PASS | F27 tests cover `"一家三口" -> household_size=3, raw="一家三口"`. |
| A14 | PASS | F27 tests cover `"三室两厅 一家四口"` with no tension notice. |
| A15 | PASS | F27 tests cover `"适合老人住" -> lifestyle`. |
| A16 | PASS | F27 tests cover `"安静一点" -> quiet_environment=True`. |
| A17 | PASS | F27 tests cover `"靠近好学校"` as unresolved, not a need. |
| A18 | PASS | Verified in backend container: enum-external need types are dropped while valid needs and unresolved text remain. |
| A19 | PASS | Verified in backend container: forcing `_interpret_needs` to raise leaves `interpreted_needs` at defaults and does not break search. |
| A20 | PASS | Verified in backend container and F27 tests: `bedrooms_min=1` + `household_size=3` yields `1室对3口之家可能偏小`. |
| A21 | PASS | Verified in backend container and F27 tests: `bedrooms_min=3` + `household_size=4` yields no tension. |
| A22 | PASS | `_detect_tensions()` is pure Python and notices are appended in `ai_search()`, not returned by `_interpret_needs()`. |
| A23 | PASS | Verified in backend container: no notice when `bedrooms_min is None`. |
| A24 | PASS | `AiSearchResult` adds `interpreted_intent` and `interpreted_needs` with default factories in `backend/app/schemas/ai_search.py`. |
| A25 | PASS | Existing `AiSearchResult` fields remain present and unchanged. |
| A26 | PASS | Verified in backend container: `docker compose run --rm backend python3 -c 'import app.main'` exits 0. |
| A27 | PASS | Verified: `cd frontend && npx tsc --noEmit` exits 0. |
| A28 | PASS | `frontend/components/features/search/interpreted-needs-card.tsx` now uses `bg-amber-50` and `text-amber-600` for tension notices, with the `⚠️` icon. |
| A29 | PASS | `filterable=false` intent renders as a dashed chip with `（暂无数据）`. |
| A30 | PASS | `need.raw` renders as gray small tags. |
| A31 | PASS | Unresolved content renders as small gray helper text. |
| A32 | PASS | The card returns `null` when notices, needs, unresolved, and non-filterable intent are all empty. |
| A33 | PASS | The UI is plain Tailwind; no shadcn components were introduced. |
| A34 | PASS | `backend/tests/eval_set_f27.json` has 8 cases spanning BUG-026, tension, fit/no-tension, pure filters, unresolved-only, mixed needs, and non-search. |
| A35 | PASS | `backend/tests/test_eval_f27.py` covers the BUG-026 `"一室两厅"` entry path. |
| A36 | PASS | `backend/tests/test_eval_f27.py` asserts the household-size tension case. |
| A37 | PASS | `bash tools/run_eval.sh` passes against the unchanged 30-case F16 eval set, and `test_eval_f26.py` also passes (`13 passed`). |
| A38 | PASS | Diffing T01 against its parent shows no edits inside `_parse_filters`. |
| A39 | PASS | The same diff shows no edits inside `_relax_filters` or `_apply_relaxation`. |

## Issues Found
- BLOCKER: Ownership boundary violation remains in feature history/current tree. T02 introduced an out-of-scope edit to `tools/run_gemini.sh`, and T04 introduced out-of-scope edits to `tools/run_codex.sh`, `tools/run_codex_review.sh`, and `tools/run_fix_codex.sh`. The feature spec’s rejection conditions treat task-scope violations as fatal even when A1-A39 pass.
- WARNING: `backend/tests/test_eval_f27.py` does not encode A18 or A19. Both behaviors work in the backend container, but the committed F27 suite does not protect them.
- MINOR: `status.json` is modified in the working tree, but the current diff and activity log attribute that state tracking to Claude orchestration rather than Codex or Gemini.

## Required Fixes
- Revert the out-of-scope harness changes in `tools/run_gemini.sh`, `tools/run_codex.sh`, `tools/run_codex_review.sh`, and `tools/run_fix_codex.sh`, or move them into an explicitly authorized task/feature before acceptance.
- Add committed F27 coverage for A18 and A19 so enum-filtering and interpretation-failure fallback are regression-protected.

## Approved Items
- The F27 product behavior is implemented correctly: BUG-026 is fixed, `living_rooms` is interpretation-only, tension notices are generated in Python, and `_interpret_needs` is isolated behind its own `try/except`.
- Frontend business logic stays in the backend. `InterpretedNeedsCard` is presentational and only renders data already shaped by the API.
- All new API contract types are published in `frontend/types/ai-search.ts`.
- `status.json` was not shown as a Codex- or Gemini-authored product change in the supplied activity log.
