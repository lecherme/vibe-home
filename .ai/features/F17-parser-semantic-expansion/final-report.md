# F17 Final Acceptance Report

## Disposition: BLOCKED — A9–A11 real-LLM confirmation incomplete

Code and review criteria (A1–A7, A12, A13) all pass. A8 confirmed end-to-end with real LLM. A9–A11 require real-LLM confirmation per acceptance.md but deepseek-v4-flash returned empty responses on this run — mapping logic is verified correct via mock (T02 review), but the acceptance criterion is not met until confirmed end-to-end.

## Criteria Results

| ID | Result | Notes |
|----|--------|-------|
| A1 | PASS | `_parse_filters` prompt requests all four subjective fields |
| A2 | PASS | Prompt explicitly prohibits `bedrooms_min/max`, `bathrooms_min/max` in LLM output |
| A3 | PASS | `_apply_subjective_room_filters`: `insufficient + N → _min = N+1`, `excessive + N → _max = N-1`, others → no filter |
| A4 | PASS | F16 values take priority via `{**sanitized_llm, **deterministic_filters}` and `is None` guards |
| A5 | PASS | `test_subjective_eval.py` exists, 8 integration cases; offline mock test runs without LLM key |
| A6 | PASS | `import app.main` exit 0 — verified in container |
| A7 | PASS | `test_eval.py` and `eval_set.json` unchanged; F16 deterministic eval 30/30 unaffected |
| A8 | PASS | "两个浴室太少" → `bathrooms_min=3` — confirmed with real LLM in container |
| A9 | NOT CONFIRMED | "三个卧室不够用 预算1500万": `max_price=15000000` correct (deterministic fallback); `bedrooms_min` not set — LLM returned empty. Mapping logic correct per mock. |
| A10 | NOT CONFIRMED | "4个卧室太多": LLM returned empty on this run (returned valid JSON in prior direct prompt test). Mapping verified via mock. |
| A11 | NOT CONFIRMED | "2 bedrooms not enough": LLM empty response. Mapping verified via mock. |
| A12 | PASS | "两个卧室刚好" → no bedrooms filter — `adequate` label produces no filter, confirmed in container |
| A13 | PASS | "3个卧室以上 预算2000万" → `bedrooms_min=3, max_price=20000000` — deterministic, no regression |

## Root Cause

deepseek-v4-flash returns empty strings for some subjective queries via the `_parse_filters` prompt. A10 returned valid JSON in a direct prompt test but failed via the full `_parse_filters` call on the same run. The LLM model is non-deterministic on this deployment.

## Path to ACCEPTED

Re-run A9–A11 manual verification after one of:
- Confirming the LLM model is returning stable non-empty responses for these queries
- Switching to a more reliable model

No code changes are needed.
