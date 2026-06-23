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
| A5 | PASS | `git diff 480ae18..51b52e0` shows `_is_property_search()` now normalizes Chinese digits before property-pattern matching. |
| A6 | PASS | Verified in backend container: `_is_property_search("为什么房价上涨") == False`. |
| A7 | PASS | Verified in backend container: `_extract_living_rooms("一室两厅") == 2`. |
| A8 | PASS | Verified in backend container: `_extract_living_rooms("三室两厅") == 2`. |
| A9 | PASS | Verified in backend container: `_extract_living_rooms("两室一厅") == 1`. |
| A10 | PASS | Verified in backend container: `_extract_living_rooms("两室") == None`. |
| A11 | PASS | `ai_search()` appends `IntentField(field="living_rooms", value=2, filterable=False)` and `backend/tests/test_eval_f27.py` asserts it. |
| A12 | PASS | `SearchFilters` has no `living_rooms` field, and `ai_search()` only surfaces it via `interpreted_intent`. |
| A13 | PASS | `backend/tests/test_eval_f27.py` covers `"一家三口" -> household_size=3, raw="一家三口"`. |
| A14 | PASS | `backend/tests/test_eval_f27.py` covers `"三室两厅 一家四口"` with no tension notice. |
| A15 | PASS | `backend/tests/test_eval_f27.py` covers `"适合老人住" -> lifestyle`. |
| A16 | PASS | `backend/tests/test_eval_f27.py` covers `"安静一点" -> quiet_environment=True`. |
| A17 | PASS | `backend/tests/test_eval_f27.py` covers `"靠近好学校"` as unresolved, not a need. |
| A18 | PASS | Verified in backend container: enum-external need types are silently dropped while valid needs/unresolved survive. |
| A19 | PASS | Verified in backend container: forcing `_interpret_needs` to raise leaves `interpreted_needs` at defaults and search flow intact. |
| A20 | PASS | Verified in backend container and F27 tests: `bedrooms_min=1` + `household_size=3` yields `1室对3口之家可能偏小`. |
| A21 | PASS | Verified in backend container and F27 tests: `bedrooms_min=3` + `household_size=4` yields no tension. |
| A22 | PASS | `_detect_tensions()` is pure Python and `_interpret_needs()` returns only `needs` and `unresolved`; notices are added later in `ai_search()`. |
| A23 | PASS | Verified in backend container: no notice when `bedrooms_min is None`. |
| A24 | PASS | [ai_search.py](/home/lecherme/workspace/vibe-home/backend/app/schemas/ai_search.py:54) adds `interpreted_intent` and `interpreted_needs` with defaults. |
| A25 | PASS | Existing `AiSearchResult` fields remain present and unchanged. |
| A26 | PASS | Verified in backend container: `import app.main` exits 0. |
| A27 | PASS | Verified: `cd frontend && npx tsc --noEmit` exits 0. |
| A28 | FAIL | [interpreted-needs-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/interpreted-needs-card.tsx:28) uses `bg-amber-50 border-amber-200 text-amber-800`; acceptance requires amber-50/amber-600 styling for the tension notice. |
| A29 | PASS | [interpreted-needs-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/interpreted-needs-card.tsx:73) renders `filterable=false` intent with dashed border and `（暂无数据）`. |
| A30 | PASS | [interpreted-needs-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/interpreted-needs-card.tsx:54) renders `need.raw` as gray small tags. |
| A31 | PASS | [interpreted-needs-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/interpreted-needs-card.tsx:87) renders unresolved text as small gray helper text. |
| A32 | PASS | [interpreted-needs-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/interpreted-needs-card.tsx:18) returns `null` when all sections are empty. |
| A33 | PASS | No shadcn imports/components were introduced; implementation is plain Tailwind. |
| A34 | PASS | `backend/tests/eval_set_f27.json` contains 8 cases spanning bug, tension, fit, unresolved, pure filters, and non-search paths. |
| A35 | PASS | `backend/tests/test_eval_f27.py` includes BUG-026 regression coverage for `"一室两厅"` entering the property-search path. |
| A36 | PASS | `backend/tests/test_eval_f27.py` asserts the household-size tension notice case. |
| A37 | PASS | `bash tools/run_eval.sh` passes, and `docker compose ... pytest /app/tests/test_eval_f26.py -q` also passes `13 passed`, including the F16 non-regression check. |
| A38 | PASS | `git diff 480ae18..51b52e0 -- backend/app/services/ai_search/service.py` shows no edits inside `_parse_filters`. |
| A39 | PASS | The same T01 diff shows no edits inside `_relax_filters` or `_apply_relaxation`. |

## Issues Found
- BLOCKER: [interpreted-needs-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/interpreted-needs-card.tsx:28) does not satisfy the required tension notice styling. The implementation uses `text-amber-800` and `border-amber-200`; the acceptance criterion explicitly calls for amber-50/amber-600 treatment.
- WARNING: `backend/tests/test_eval_f27.py` does not encode A18 or A19. Both behaviors work when exercised directly in the backend container, but they are not protected by the committed F27 test suite.
- MINOR: `.ai/features/F27-need-interpretation/status.json` is modified in the working tree, but the diff and activity log attribute those changes to Claude orchestration, not Codex or Gemini.

## Required Fixes
- Update the tension notice styling in [interpreted-needs-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/interpreted-needs-card.tsx:28) to use the required amber-50/amber-600 visual treatment so A28 passes.

## Approved Items
- Backend implementation matches the F27 scope: BUG-026 is fixed, `living_rooms` is interpretation-only, notices are generated in Python, and `_interpret_needs` is isolated behind its own `try/except`.
- Ownership boundaries were respected in T01/T02/T03, and the protected backend helpers remained unchanged.
- All new API types were published to `frontend/types/ai-search.ts`.
- Frontend business logic remains in the backend; `InterpretedNeedsCard` is presentational only.
- `status.json` was not modified by Codex or Gemini based on the working-tree diff and activity log.
