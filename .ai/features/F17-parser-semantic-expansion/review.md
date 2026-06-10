# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | `_parse_filters` prompt requests `bedrooms_subjective_label`, `bedrooms_ref`, `bathrooms_subjective_label`, and `bathrooms_ref` in [backend/app/services/ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:237). |
| A2 | PASS | The prompt explicitly tells the LLM not to return `bedrooms_min/max`, `bathrooms_min/max`, `min_price`, or `max_price` in [backend/app/services/ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:239). |
| A3 | PASS | `insufficient` maps to `ref + 1`, `excessive` maps to `ref - 1`, and other labels are no-ops because only those two labels are handled in [backend/app/services/ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:208). |
| A4 | PASS | Subjective mapping checks whether the deterministic target bound is already set before writing it in [backend/app/services/ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:213). |
| A5 | PASS | `backend/tests/test_subjective_eval.py` exists, has 8 cases, and is marked `@pytest.mark.integration` at module scope in [backend/tests/test_subjective_eval.py](/home/lecherme/workspace/vibe-home/backend/tests/test_subjective_eval.py:14). |
| A6 | PASS | `docker compose exec backend python -c "import app.main; print('OK')"` returned `OK`. |
| A7 | PASS | F16 deterministic eval still passes at 100%: 30/30 cases from `backend/tests/eval_set.json` passed when re-evaluated inside the backend container against `_normalize_query`. |
| A8 | PASS | Backend coverage exists for `"两个浴室太少"` -> `bathrooms_min=3` in [backend/tests/test_subjective_eval.py](/home/lecherme/workspace/vibe-home/backend/tests/test_subjective_eval.py:26). Frontend was untouched. |
| A9 | PASS | Backend coverage exists for `"3间卧室不够 预算1500w"` -> `bedrooms_min=4`, `max_price=15000000` in [backend/tests/test_subjective_eval.py](/home/lecherme/workspace/vibe-home/backend/tests/test_subjective_eval.py:32). Frontend was untouched. |
| A10 | PASS | Backend coverage exists for `"4个卧室太多"` -> `bedrooms_max=3` in [backend/tests/test_subjective_eval.py](/home/lecherme/workspace/vibe-home/backend/tests/test_subjective_eval.py:28). |
| A11 | PASS | Backend coverage exists for `"2 bedrooms not enough"` -> `bedrooms_min=3` in [backend/tests/test_subjective_eval.py](/home/lecherme/workspace/vibe-home/backend/tests/test_subjective_eval.py:29). |
| A12 | PASS | `adequate` yields no filter by inspection because only `insufficient` and `excessive` write bounds in [backend/app/services/ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:213). |
| A13 | PASS | No F16 regression was observed: `backend/tests/test_eval.py` and `backend/tests/eval_set.json` are unchanged, and the eval ratio is 100%. |
| Boundary Rule 1 | PASS | No evidence that Codex or Gemini modified `status.json`; its activity log entries are all authored by `claude` in [.ai/features/F17-parser-semantic-expansion/status.json](/home/lecherme/workspace/vibe-home/.ai/features/F17-parser-semantic-expansion/status.json:44). |
| Boundary Rule 2 | FAIL | The code does not enforce the invariant that the LLM cannot set bounds directly. `_apply_subjective_room_filters` starts from the raw LLM payload and `_normalize_filters` later accepts bound keys from that merged dict in [backend/app/services/ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:192) and [backend/app/services/ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:259). I reproduced this by stubbing `complete()` to return `{\"bedrooms_min\":99}`; `_parse_filters(\"Central\")` returned `bedrooms_min=99`. |
| Boundary Rule 3 | PASS | `backend/tests/eval_set.json` and `backend/tests/test_eval.py` were not modified. |
| Frontend Logic | PASS | No frontend files changed, so no business logic was moved into frontend components. |
| API Types Published | PASS | No backend schema or API type surface changed, so no `frontend/types/` publication was required. |

## Issues Found
- BLOCKER: The implementation trusts extra bound fields from the LLM payload. Because `merged_filters = {**raw_filters, **deterministic_filters}` is passed into `_normalize_filters`, a model response containing forbidden keys like `bedrooms_min`, `bedrooms_max`, `bathrooms_min`, `bathrooms_max`, `min_price`, or `max_price` can still directly set filters when the deterministic parser did not already set them. This violates the F17 invariant and Boundary Rule 2. Repro: stub `complete()` to return `{"location":"Central","bedrooms_min":99}` and `_parse_filters("Central")` produces `bedrooms_min=99`.
- MINOR: There is no regression test asserting that forbidden direct bound keys from the LLM are ignored, so this boundary can regress silently.

## Required Fixes
- Strip or whitelist the LLM payload before normalization so only `location`, `status`, `remainder`, `bedrooms_subjective_label`, `bedrooms_ref`, `bathrooms_subjective_label`, and `bathrooms_ref` are accepted from the model.
- Add a test that mocks/stubs the LLM response with forbidden direct bound keys and asserts `_parse_filters` ignores them.

## Approved Items
- The prompt extension for subjective bedroom and bathroom labels/refs is implemented correctly.
- The deterministic mapping rules and F16 priority behavior are implemented correctly.
- `backend/tests/test_subjective_eval.py` satisfies the required coverage shape and integration marking.
- `import app.main` succeeds in the backend container.
- F16 deterministic parsing remains intact at 100% on the current eval set.
- No frontend files, backend schema files, `test_eval.py`, or `eval_set.json` were changed.
- No evidence shows `status.json` was modified by Codex or Gemini.
