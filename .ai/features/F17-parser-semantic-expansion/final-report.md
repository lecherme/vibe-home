# F17 Final Acceptance Report

## Disposition: ACCEPTED

All criteria pass. Code verified end-to-end with real LLM (deepseek-v4-pro, thinking disabled).

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
| A8 | PASS | "两个浴室太少" → `bathrooms_min=3` — confirmed with real LLM |
| A9 | PASS | "三个卧室不够用 预算1500万" → `bedrooms_min=4, max_price=15000000` — confirmed with real LLM |
| A10 | PASS | "4个卧室太多" → `bedrooms_max=3` — confirmed with real LLM |
| A11 | PASS | "2 bedrooms not enough" → `bedrooms_min=3` — confirmed with real LLM |
| A12 | PASS | "两个卧室刚好" → no bedrooms filter — `adequate` label produces no filter |
| A13 | PASS | "3个卧室以上 预算2000万" → `bedrooms_min=3, max_price=20000000` — deterministic, no regression |

## Fix Applied During Acceptance

deepseek-v4-pro defaults to thinking mode, consuming all `max_tokens` on `reasoning_content` before writing JSON. Fixed by adding `disable_thinking=True` to the `_parse_filters` → `complete()` call path, which passes `extra_body={"thinking": {"type": "disabled"}}` and `temperature=1` to the API. Non-DeepSeek providers are unaffected (parameter not forwarded on `anthropic`/`openai` paths).
