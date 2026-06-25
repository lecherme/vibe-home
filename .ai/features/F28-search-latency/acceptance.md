# F28 — Acceptance Criteria

T06 (Codex review) verifies every criterion below and writes `review.md`.
T07 (Claude acceptance) reads `review.md` and writes `final-report.md`.

---

## Instrumentation

| ID | Criterion |
|----|-----------|
| A1 | After any property search, a structured INFO log entry is emitted with field `parse_filters_ms` (integer) |
| A2 | Same log entry contains `interpret_needs_ms`, `resolve_ids_ms`, `collect_items_ms`, `total_ms` (all integers) |
| A3 | Same log entry contains `query` field for correlation |
| A4 | Log entry is emitted at the END of `ai_search()`, not mid-function |

## Parallelization

| ID | Criterion |
|----|-----------|
| A5 | `_interpret_needs` and `_resolve_result_ids` are both submitted to a `ThreadPoolExecutor` before either `.result()` is awaited |
| A6 | Test asserts that both futures are created before either result is retrieved |
| A7 | When `_interpret_needs` raises an exception, `_resolve_result_ids` result is still used and the search returns normally with empty `interpreted_needs` |
| A8 | Test covers the `_interpret_needs` failure-isolation path |

## Non-regression

| ID | Criterion |
|----|-----------|
| A9 | `bash tools/run_eval.sh` exits 0 (F16 eval unchanged) |
| A10 | F27 eval passes: `docker compose run --rm -v $(pwd)/backend/tests:/app/tests backend python3 -m pytest /app/tests/test_eval_f27.py -q` exits 0 |

---

## Review and Acceptance

If review verdict is FAIL, Claude does NOT proceed directly to T07 acceptance.
Claude must:
1. Write `last_review_failure` to `status.json` with fix_path, failed_criteria, and fix_instructions.
2. Choose fix_path: task_retry, direct_fixup, or review_rerun.
3. Apply the fix and re-run review before acceptance.

## Rejection Conditions

- Any worker modifies `status.json`
- Any changes to `frontend/`, `backend/app/schemas/`, or `backend/app/api/`
- Any summary decoupling code present (TTLCache, UUID, summary endpoint) — deferred to F29
- F16 or F27 eval regresses
