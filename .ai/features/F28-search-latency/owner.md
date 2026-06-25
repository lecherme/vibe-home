# F28 — Owner Map

## Codex (T01, T02, T05, T06)

### T01 — Instrumentation
- `backend/app/services/ai_search/service.py`: add `time.perf_counter()` timing around `_parse_filters`, `_interpret_needs`, `_resolve_result_ids`, `_collect_items`; emit structured log at end of `ai_search()`

### T02 — Parallelization
- `backend/app/services/ai_search/service.py`: replace serial `_interpret_needs` → `_resolve_result_ids` with concurrent `ThreadPoolExecutor` submission
- `backend/tests/test_f28_latency.py`: tests for concurrent submission and failure isolation

### T05 — Non-regression
- Read-only: runs `bash tools/run_eval.sh` (F16) and F27 pytest suite; documents pass/fail

### T06 — Review
- Reviews all implementation artifacts against acceptance criteria

### Forbidden for Codex
- Do NOT modify `frontend/` (no frontend changes in F28)
- Do NOT modify `backend/app/schemas/`, `backend/app/api/` (no schema or router changes in F28)
- Do NOT modify `backend/tests/eval_set.json`, `test_eval.py`, `eval_set_f27.json`, `test_eval_f27.py`
- Do NOT modify `status.json`
- Do NOT implement summary decoupling, TTLCache, UUID generation, or summary endpoint (deferred to F29)

---

## No Gemini tasks in F28
F28 has no frontend changes. Gemini is not used in this feature.
