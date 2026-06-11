# F18 Final Report

## Verdict
ACCEPTED

## Criteria Results

| ID | Criterion | Result | Notes |
|----|-----------|--------|-------|
| A1 | `_BATHROOM_PATTERN` includes `卫生间` and `洗手间` | PASS | `service.py:27`: `(?:卫生间\|洗手间\|浴室\|bathrooms?\|baths?)` |
| A2 | `室`/`卧` only in digit-bounded patterns | PASS | `_BEDROOM_PATTERN` at `:26` has no `室`/`卧`; shorthand via `_extract_shorthand_comparator` at `:148-194` only |
| A3 | `卫` only in digit-bounded patterns | PASS | `_BATHROOM_PATTERN` at `:27` has no free `卫`; shorthand via `_extract_shorthand_comparator` only |
| A4 | Bare-count step exists, after comparator extraction, maps N → `_min` | PASS | `_extract_bare_count` at `:196-215`, applied after all comparator passes at `:144-194` |
| A5 | `test_eval.py` and `eval_set.json` unchanged; F16 eval 30/30 | PASS | `git diff HEAD -- backend/tests/test_eval.py backend/tests/eval_set.json` empty; F16 30/30 confirmed in container |
| A6 | `3个卫生间以上` → `bathrooms_min=3` | PASS | Verified in container |
| A7 | `2卫以下` → `bathrooms_max=2` | PASS | Verified in container |
| A8 | `2个卧室 预算2000万` → `bedrooms_min=2, max_price=20000000` | PASS | Verified in container |
| A9 | `3室以上` → `bedrooms_min=3` | PASS | Verified in container |
| A10 | `2卧以下` → `bedrooms_max=2` | PASS | Verified in container |
| A11 | `2个浴室` → `bathrooms_min=2` | PASS | Verified in container |
| A12 | `2 bedrooms` → `bedrooms_min=2` | PASS | Verified in container |
| A13 | `3卫 预算1500w` → `bathrooms_min=3, max_price=15000000` | PASS | Verified in container |
| A14 | `3个卫生间以上 不超过2000w` → `bathrooms_min=3, max_price=20000000` | PASS | Verified in container |
| A15 | `3个卧室以上 预算2000万` → `bedrooms_min=3, max_price=20000000` | PASS | Verified in container |
| A16 | `两个浴室太少` → `bathrooms_min=3` | PASS | `_SUBJECTIVE_BLOCKER` prevents bare-count from consuming `两个浴室`; F17 path raises to min=3 |

## Summary

F18 is complete. All 16 acceptance criteria pass.

The deterministic parser now recognizes:
- `卫生间` and `洗手间` as bathroom synonyms (A1)
- `N室`/`N卧`/`N卫` shorthand with comparators, digit-bounded only (A2/A3)
- Bare room counts `N个卧室`, `N室`, `N卧`, `N个浴室`, `N卫`, `N bedrooms`, `N baths` → `_min=N` (A4)
- `_SUBJECTIVE_BLOCKER` prevents bare-count extraction inside subjective phrases like `太少`/`too few` (A16)

F16 eval unchanged at 30/30.
