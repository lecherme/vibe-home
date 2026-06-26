# F30 — Acceptance Criteria

T03 (Codex review) verifies every criterion below and writes `review.md`.
T04 (Claude acceptance) reads `review.md` and writes `final-report.md`.

---

## Embedding and semantic search reuse

| ID | Criterion |
|----|-----------|
| A1 | For parsed property searches with non-empty query, `embed_text(query)` is called at most once per `ai_search()` invocation — the result is passed into downstream calls, not recomputed |
| A2 | `_apply_relaxation()` does not call `_resolve_result_ids()` or `embed_text()` or `semantic_search()` internally; it accepts pre-computed semantic ranked IDs and re-applies filters only |
| A3 | Test or code inspection confirms no second embedding call occurs during relaxation |

## Batch property fetch

| ID | Criterion |
|----|-----------|
| A4 | The per-ID `get_by_id()` loop for strict-candidate filtering is replaced by a single batch fetch |
| A5 | The per-ID `get_by_id()` loop for relaxed-candidate filtering is replaced by a single batch fetch |

## Internal relaxation timing

| ID | Criterion |
|----|-----------|
| A6 | `logger.info("AI search timing", ...)` emits `strict_filtering_ms` (integer) |
| A7 | Same log emits `apply_relaxation_ms` (integer) |
| A8 | Same log emits `relaxed_filtering_ms` (integer) |
| A9 | Same log emits `relaxation_steps` (integer — count of relaxation iterations attempted) |
| A10 | `logging.py` whitelist includes all four new fields |

## Non-regression

| ID | Criterion |
|----|-----------|
| A11 | `bash tools/run_eval.sh` exits 0 (F16 eval unchanged) |
| A12 | F27 eval passes: `docker compose run --rm -v $(pwd)/backend/tests:/app/tests backend python3 -m pytest /app/tests/test_eval_f27.py -q` exits 0 with 28 passed |

---

## Review and Acceptance

If review verdict is FAIL, Claude does NOT proceed directly to T04 acceptance.
Claude must:
1. Write `last_review_failure` to `status.json` with fix_path, failed_criteria, and fix_instructions.
2. Choose fix_path: task_retry, direct_fixup, or review_rerun.
3. Apply the fix and re-run review before acceptance.

## Rejection Conditions

- Any worker modifies `status.json`
- Any changes to `frontend/`, `backend/app/schemas/`, or `backend/app/api/`
- F16 or F27 eval regresses
- `embed_text(query)` or `semantic_search()` still called more than once per `ai_search()` for parsed property searches
