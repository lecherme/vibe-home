# Codex Build Report

## Task Completed
- T01

## Files Changed
- `backend/app/services/ai_search/service.py`
- `backend/tests/test_subjective_eval.py` (new)

## API Types Published
- None

## Tests Written
- `backend/tests/test_subjective_eval.py` — 8 integration cases, `@pytest.mark.integration`, skipped without LLM API key

## Summary

Added `_apply_subjective_room_filters(raw_filters, deterministic_filters)` to `ai_search/service.py`:
- Reads `bedrooms_subjective_label`, `bedrooms_ref`, `bathrooms_subjective_label`, `bathrooms_ref` from LLM output
- `insufficient` + N → `_min = N + 1` (only if F16 deterministic did not already set the field)
- `excessive` + N → `_max = N - 1` (only if F16 deterministic did not already set the field)
- `adequate`, `unknown`, or null ref → no filter

Extended `_parse_filters` LLM prompt to request four new fields. Prompt explicitly instructs LLM not to return `bedrooms_min/max`, `bathrooms_min/max` directly. Updated call path to use `_apply_subjective_room_filters`.

## Verification

`docker compose exec backend python -c "import app.main; print('OK')"` → OK

## Open Issues

Codex session disconnected before stdout capture; code changes were written to disk and verified by Claude. Integration tests in `test_subjective_eval.py` require a live LLM API key and cannot run in the standard backend container test suite.
