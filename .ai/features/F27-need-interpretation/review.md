# Review

## Verdict
PASS

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | Verified in backend container: `_is_property_search("一室两厅") == True`. |
| A2 | PASS | Verified in backend container: `_is_property_search("一室两厅 一家三口") == True`. |
| A3 | PASS | Verified in backend container: `_is_property_search("两房一厅") == True`. |
| A4 | PASS | Verified in backend container: `_is_property_search("三室两卫") == True`. |
| A5 | PASS | `_is_property_search()` normalizes Chinese digits before `_PROPERTY_SEARCH_PATTERNS`, and the room-count regex now includes `厅`. |
| A6 | PASS | Verified in backend container: `_is_property_search("为什么房价上涨") == False`. |
| A7 | PASS | Verified in backend container: `_extract_living_rooms("一室两厅") == 2`. |
| A8 | PASS | Verified in backend container: `_extract_living_rooms("三室两厅") == 2`. |
| A9 | PASS | Verified in backend container: `_extract_living_rooms("两室一厅") == 1`. |
| A10 | PASS | Verified in backend container: `_extract_living_rooms("两室") == None`. |
| A11 | PASS | `ai_search()` appends `IntentField(field="living_rooms", value=2, filterable=False)`; F27 tests assert the emitted payload. |
| A12 | PASS | `living_rooms` is only surfaced through `interpreted_intent`; it is not written into `SearchFilters`, and `_parse_filters` was not changed. |
| A13 | PASS | F27 eval/test case covers `"一家三口"` -> `household_size=3`, raw `"一家三口"`. |
| A14 | PASS | F27 eval/test case covers `"三室两厅 一家四口"` -> `household_size=4` with no tension notice. |
| A15 | PASS | F27 eval/test case covers `"适合老人住"` -> `lifestyle`. |
| A16 | PASS | F27 eval/test case covers `"安静一点"` -> `quiet_environment=True`. |
| A17 | PASS | F27 eval/test case covers `"靠近好学校"` as unresolved text, not a need. |
| A18 | PASS | `backend/tests/test_eval_f27.py` now includes `test_interpret_needs_discards_unknown_type`. |
| A19 | PASS | `backend/tests/test_eval_f27.py` now includes `test_ai_search_interpret_needs_exception_returns_empty_default`. |
| A20 | PASS | Verified in backend container and F27 suite: `bedrooms_min=1` + `household_size=3` yields `1室对3口之家可能偏小`. |
| A21 | PASS | Verified in backend container and F27 suite: `bedrooms_min=3` + `household_size=4` yields no tension. |
| A22 | PASS | `_detect_tensions()` is pure Python, and notices are attached in `ai_search()` after `_interpret_needs()` returns. |
| A23 | PASS | Verified in backend container: no notice is generated when `bedrooms_min is None`. |
| A24 | PASS | `AiSearchResult` adds `interpreted_intent` and `interpreted_needs` with default factories in `backend/app/schemas/ai_search.py`. |
| A25 | PASS | Existing `AiSearchResult` fields remain present and unchanged. |
| A26 | PASS | Verified in backend container: `docker compose run --rm backend python3 -c 'import app.main; print("ok")'` prints `ok`. |
| A27 | PASS | Verified: `cd frontend && npx tsc --noEmit` exits 0. |
| A28 | PASS | `InterpretedNeedsCard` uses `bg-amber-50` and `text-amber-600` for tension notices and renders the `⚠️` icon. |
| A29 | PASS | `filterable=false` intent renders as a dashed chip with `（暂无数据）`. |
| A30 | PASS | `need.raw` renders as gray small tags. |
| A31 | PASS | Unresolved content renders as small gray helper text. |
| A32 | PASS | The component returns `null` when notices, needs, unresolved, and non-filterable intent are all empty. |
| A33 | PASS | The UI uses Tailwind classes only; no shadcn components were introduced. |
| A34 | PASS | `backend/tests/eval_set_f27.json` contains 8 cases covering BUG-026, tension, no-tension, pure filters, mixed needs, unresolved-only, and non-search. |
| A35 | PASS | `backend/tests/test_eval_f27.py` includes the BUG-026 `bug_026_entry` search-pipeline regression case. |
| A36 | PASS | `backend/tests/test_eval_f27.py` asserts the `household_size=3` + `bedrooms_min=1` tension case. |
| A37 | PASS | `bash tools/run_eval.sh` exits 0, and direct container verification shows `backend/tests/eval_set.json` passes `30/30`. |
| A38 | PASS | Diffing `ba535a5..51b52e0` shows no edits inside `_parse_filters`. |
| A39 | PASS | The same diff shows no edits inside `_relax_filters` or `_apply_relaxation`. |

## Issues Found
- None.

## Required Fixes
- None.

## Approved Items
- Backend implementation matches the F27 product behavior: BUG-026 is fixed, `living_rooms` is interpretation-only, need interpretation is isolated behind its own `try/except`, and tensions are generated in Python.
- Frontend business logic remains in the backend. `InterpretedNeedsCard` is presentational and only renders API-provided data.
- All new API contract types are published in `frontend/types/ai-search.ts`.
- `status.json` is currently modified only by Claude orchestration state updates per the activity log; there is no evidence of Codex- or Gemini-authored state-file changes.
- Scope review passes for the current implementation set. Runtime-authorized `tools/*.sh` changes are not flagged, and the transient `install.sh` addition is not present in the current tree.
