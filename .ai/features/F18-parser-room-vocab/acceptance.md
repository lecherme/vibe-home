# F18 Acceptance Criteria

## Structural (A1–A5) — verifiable by code inspection

| ID | Criterion |
|----|-----------|
| A1 | `_BATHROOM_PATTERN` includes `卫生间` and `洗手间` |
| A2 | `室` and `卧` are supported only inside digit-bounded extraction patterns, not as free alternations in `_BEDROOM_PATTERN` |
| A3 | `卫` is supported only inside digit-bounded extraction patterns, not as a free alternation in `_BATHROOM_PATTERN` |
| A4 | A bare-count extraction step exists, applied after comparator-based extraction, mapping `N + room noun (no comparator)` → `_min = N` |
| A5 | `test_eval.py` and `eval_set.json` unchanged; F16 eval 30/30 unaffected |

## Functional (A6–A14) — verified via `_parse_filters` in container

| ID | Query | Expected |
|----|-------|----------|
| A6 | `3个卫生间以上` | `bathrooms_min=3` |
| A7 | `2卫以下` | `bathrooms_max=2` |
| A8 | `2个卧室 预算2000万` | `bedrooms_min=2, max_price=20000000` |
| A9 | `3室以上` | `bedrooms_min=3` |
| A10 | `2卧以下` | `bedrooms_max=2` |
| A11 | `2个浴室` | `bathrooms_min=2` |
| A12 | `2 bedrooms` | `bedrooms_min=2` |
| A13 | `3卫 预算1500w` | `bathrooms_min=3, max_price=15000000` |
| A14 | `3个卫生间以上 不超过2000w` | `bathrooms_min=3, max_price=20000000` |

## Regression (A15–A16)

| ID | Query | Expected |
|----|-------|----------|
| A15 | `3个卧室以上 预算2000万` | `bedrooms_min=3, max_price=20000000` |
| A16 | `两个浴室太少` | `bathrooms_min=3` |
