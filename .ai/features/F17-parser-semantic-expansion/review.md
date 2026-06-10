# Review

## Verdict
PASS

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | `_parse_filters` prompt requests `bedrooms_subjective_label`, `bedrooms_ref`, `bathrooms_subjective_label`, and `bathrooms_ref` in `backend/app/services/ai_search/service.py`. |
| A2 | PASS | The prompt explicitly forbids direct LLM output of `bedrooms_min/max`, `bathrooms_min/max`, `min_price`, and `max_price`. |
| A3 | PASS | `_apply_subjective_room_filters()` maps `insufficient -> ref + 1`, `excessive -> ref - 1`, and leaves other labels as no-ops. |
| A4 | PASS | F16 deterministic values retain priority via the `deterministic_filters.get(...) is None` guards before subjective writes. |
| A5 | PASS | `backend/tests/test_subjective_eval.py` exists, contains 8 integration cases, and the live-LLM parametrized test is marked `@pytest.mark.integration`. |
| A6 | PASS | Recorded verification in feature artifacts shows `docker compose exec backend python -c "import app.main; print('OK')"` returned `OK`. |
| A7 | PASS | Prior review artifact recorded F16 eval at 30/30 passing; current rerun only changes skip placement in `backend/tests/test_subjective_eval.py`, not `_normalize_query`, `test_eval.py`, or `eval_set.json`. |
| A8 | PASS | Backend test coverage includes `"两个浴室太少" -> bathrooms_min=3`, and the existing frontend chip renders min bathrooms as `>= X Baths`. |
| A9 | PASS | Backend test coverage includes the combined case `"3间卧室不够 预算1500w" -> bedrooms_min=4, max_price=15000000`, and the frontend chip formatting matches `>=` beds plus `<` price. |
| A10 | PASS | Backend test coverage includes `"4个卧室太多" -> bedrooms_max=3`, and the frontend chip renders max bedrooms as `<= X Beds`. |
| A11 | PASS | Backend test coverage includes `"2 bedrooms not enough" -> bedrooms_min=3`. |
| A12 | PASS | `adequate` produces no bound because only `insufficient` and `excessive` write filters; the frontend only renders room chips when min/max exists. |
| A13 | PASS | No F16 regression surface was modified: `backend/tests/test_eval.py` and `backend/tests/eval_set.json` are unchanged, and prior recorded eval remained 100%. |
| Boundary Rule 1 | PASS | `status.json` is modified in the worktree, but the activity log attributes those updates to `claude`; no evidence shows Codex or Gemini changed it. |
| Boundary Rule 2 | PASS | The LLM payload is now whitelisted by `_LLM_ALLOWED_KEYS`, and the offline mocked test asserts forbidden bound keys are ignored. |
| Boundary Rule 3 | PASS | `backend/tests/test_eval.py` and `backend/tests/eval_set.json` were not modified. |
| Frontend Logic | PASS | No frontend files were changed, so no business logic was moved into frontend components. |
| API Types Published | PASS | No backend schema/API surface changed, so no new `frontend/types/` publication was required. |

## Issues Found
- WARNING: Automated coverage still does not include an explicit `adequate` or `unknown` subjective case, nor a direct regression test for F16-vs-F17 precedence on the same room field. The implementation is correct by inspection, but those edge cases remain manually validated rather than test-protected.

## Required Fixes
- None.

## Approved Items
- The prompt extension matches the controlled subjective schema.
- The deterministic mapping step is implemented in backend service code, not frontend components.
- Forbidden direct bound keys from the LLM are stripped before normalization.
- The retry reason is resolved: the mocked forbidden-bounds test now runs outside the LLM-key-gated integration path.
- Scope stayed within the authorized backend file plus the new backend test file; no schema, frontend, `test_eval.py`, `eval_set.json`, or user-owned feature state files were changed by Codex.
