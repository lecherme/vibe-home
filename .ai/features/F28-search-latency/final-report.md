## Disposition: ACCEPTED

# F28 Search Latency Pass — Final Acceptance Report

T06 Codex review verdict: **PASS** (all A1–A10 criteria passed, no issues found, no required fixes).

## Criteria Verification

| ID | Criterion | Result | Evidence |
|----|-----------|--------|----------|
| A1 | Structured log emits `parse_filters_ms` (integer) | PASS | service.py:1286 |
| A2 | Same log contains `interpret_needs_ms`, `resolve_ids_ms`, `collect_items_ms`, `total_ms` | PASS | service.py:1286 |
| A3 | Log contains `query` field | PASS | service.py:1294 |
| A4 | Log emitted at end of `ai_search()`, not mid-function | PASS | Codex verified — emitted immediately before final return |
| A5 | Both futures submitted to ThreadPoolExecutor before either `.result()` awaited | PASS | service.py:1181 |
| A6 | Test asserts submit-submit-result ordering | PASS | test_f28_latency.py:24 — `test_ai_search_submits_interpret_and_resolve_before_waiting` |
| A7 | `_interpret_needs` exception → `_resolve_result_ids` result still used, search returns normally | PASS | service.py:1185 |
| A8 | Test covers `_interpret_needs` failure-isolation path | PASS | test_f28_latency.py:77 — `test_ai_search_uses_resolved_ids_when_interpretation_fails` |
| A9 | `bash tools/run_eval.sh` exits 0 (F16 unchanged) | PASS | 2 passed — verified in review |
| A10 | F27 eval 28/28 passes | PASS | 28 passed — verified in review |

## Notes
- T03 (summary decoupling) and T04 (frontend deferred summary UI) were attempted, then reverted after T05 detected a real F27 contract regression (`ai_summary` empty string broke existing test contract). Summary decoupling is deferred to F29 where it can be implemented cleanly with SSE.
- F28 delivers: per-stage latency instrumentation + concurrent execution of `_interpret_needs` and `_resolve_result_ids`, saving ~3–15 s per search depending on LLM/Supabase response times.
- No frontend, schema, or API changes. No F27 contract changes.
