# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | `_parse_filters` now requests `bedrooms_subjective_label`, `bedrooms_ref`, `bathrooms_subjective_label`, and `bathrooms_ref` in `backend/app/services/ai_search/service.py:245-258`. |
| A2 | PASS | The prompt explicitly forbids direct bound output and only allows `location`, `status`, `remainder`, and the four subjective fields in `backend/app/services/ai_search/service.py:247-252`. |
| A3 | PASS | Subjective mapping is deterministic: `insufficient -> min = N + 1`, `excessive -> max = N - 1`, others no-op in `backend/app/services/ai_search/service.py:216-227`. |
| A4 | PASS | F16 deterministic values retain priority via `merged_filters = {**sanitized_llm, **deterministic_filters}` plus the `is None` guards before setting min/max in `backend/app/services/ai_search/service.py:199-224`. |
| A5 | PASS | `backend/tests/test_subjective_eval.py` exists, is marked `@pytest.mark.integration`, and contains 8 subjective integration cases at `backend/tests/test_subjective_eval.py:17-43`. |
| A6 | PASS | `docker compose exec backend python -c "import app.main; print('OK')"` returned `OK`. |
| A7 | PASS | No F17 changes touch `_normalize_query` or `backend/tests/test_eval.py`; F16 deterministic logic remains unchanged. The spec’s containerized pytest path was not reproducible here because `/app` does not contain `tests/`, but this does not indicate a regression in the reviewed code. |

## Issues Found
- BLOCKER: `backend/tests/test_subjective_eval.py:17-23` applies a file-level `skipif` requiring a live LLM API key to every test in the module, so the new mocked regression test at `backend/tests/test_subjective_eval.py:46-67` is skipped in no-key environments even though it patches `complete()` and should run offline. The retry reason was to add a guard for forbidden bound keys; as written, that guard is not reliably exercised.
- WARNING: The verification command `docker compose exec backend python -m pytest tests/test_eval.py -v` does not work in this environment because the backend container image at `/app` does not include `tests/`. That is an environment/layout issue, not a code defect.

## Required Fixes
- Move `test_llm_forbidden_bound_keys_are_stripped` out from under the module-level API-key skip, or override the skip for that test, so the forbidden-bound regression guard runs without a live LLM key.

## Approved Items
- The retry fix for whitelisting LLM keys is correctly implemented in `backend/app/services/ai_search/service.py:188-200`; direct `bedrooms_min/max` and `bathrooms_min/max` values from the LLM are stripped before normalization.
- No frontend files were changed, so no business logic was moved into frontend components.
- No API schema/types changed under `backend/app/schemas/`, so no `frontend/types/` publication was required.
- `status.json` is modified in the worktree, but the activity log attributes those updates to `claude`; there is no evidence of Codex or Gemini modifying it.
