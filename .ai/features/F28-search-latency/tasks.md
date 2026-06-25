# F28 Tasks

## T01
**title**: Instrumentation — per-stage timing in ai_search()
**owner**: codex
**type**: build
**depends_on**: —

**Scope**:
- `backend/app/services/ai_search/service.py`

**Done condition**:
After any property search completes, a structured INFO log entry is emitted at the end of `ai_search()` containing fields `parse_filters_ms`, `interpret_needs_ms`, `resolve_ids_ms`, `collect_items_ms`, `total_ms`, and `query` (all ms fields are integers).

**Verification**:
`docker compose exec -T backend python3 -c "import app.main; print('OK')"`

---

## T02
**title**: Parallelize `_interpret_needs` + `_resolve_result_ids`
**owner**: codex
**type**: build
**depends_on**: T01

**Scope**:
- `backend/app/services/ai_search/service.py`
- `backend/tests/test_f28_latency.py`

**Done condition**:
`_interpret_needs` and `_resolve_result_ids` are submitted to a `ThreadPoolExecutor` concurrently immediately after `_parse_filters` completes. Both futures are submitted before either `.result()` is called. An exception in `_interpret_needs` falls to the empty-default path and does not prevent use of the `_resolve_result_ids` result. Tests cover: (1) concurrent future submission, (2) `_interpret_needs` failure isolation.

**Verification**:
`docker compose run --rm -v $(pwd)/backend/tests:/app/tests backend python3 -m pytest /app/tests/test_f28_latency.py -q`

---

## T05
**title**: Non-regression eval — F16 + F27
**owner**: codex
**type**: build
**depends_on**: T01, T02

**Scope**: (read-only — no source files modified)

**Done condition**:
`bash tools/run_eval.sh` exits 0 (F16 eval) and F27 eval exits 0. Results documented in build report.

**Verification**:
`bash tools/run_eval.sh`

---

## T06
**title**: Codex review
**owner**: codex
**type**: review
**depends_on**: T01, T02, T05

---

## T07
**title**: Claude acceptance
**owner**: claude
**type**: acceptance
**depends_on**: T06
