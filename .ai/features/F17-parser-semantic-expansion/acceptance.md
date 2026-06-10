# F17 Acceptance Criteria

## Backend (T01)

| ID | Criterion |
|----|-----------|
| A1 | LLM prompt in `_parse_filters` requests `bedrooms_subjective_label`, `bedrooms_ref`, `bathrooms_subjective_label`, `bathrooms_ref` |
| A2 | LLM prompt does **not** request `bedrooms_min`, `bedrooms_max`, `bathrooms_min`, `bathrooms_max` directly |
| A3 | Mapping step: `insufficient + N` → `_min = N + 1`; `excessive + N` → `_max = N - 1`; others → no filter |
| A4 | F16 deterministic values take priority: subjective mapping does not overwrite already-set fields |
| A5 | `test_subjective_eval.py` exists, has >= 8 cases, marked `@pytest.mark.integration` |
| A6 | `python -c "import app.main"` exit 0 |
| A7 | `test_eval.py` (F16 deterministic) still passes at >= 80% |

## Manual (T03 Claude)

| ID | Criterion |
|----|-----------|
| A8 | "两个浴室太少" → filter chip shows `>= 3 Baths` |
| A9 | "三个卧室不够用 预算1500万" → filter chips show `>= 4 Beds` + `< $15000000` |
| A10 | "4个卧室太多" → filter chip shows `<= 3 Beds` |
| A11 | "2 bedrooms not enough" → filter chip shows `>= 3 Beds` |
| A12 | "两个卧室刚好" → no bedrooms filter chip (adequate = no filter) |
| A13 | Existing F16 explicit comparator queries unaffected (no regression) |
