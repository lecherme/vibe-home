# F28 — Owner Map

## Codex (T01, T02, T03, T05, T06)

### T01 — Instrumentation
- `backend/app/services/ai_search/service.py`: add `time.perf_counter()` timing around `_parse_filters`, `_interpret_needs`, `_resolve_result_ids`, `_collect_items` stages; emit structured log at end of `ai_search()`

### T02 — Parallelization
- `backend/app/services/ai_search/service.py`: replace serial `_interpret_needs` → `_resolve_result_ids` with concurrent `ThreadPoolExecutor` submission
- `backend/tests/test_f28_latency.py`: tests for concurrent submission and failure isolation

### T03 — Summary decoupling
- `backend/app/services/ai_search/service.py`: add TTLCache context store, UUID generation, remove `_generate_summary` call, add `search_request_id` to return
- `backend/app/api/v1/ai_search/router.py`: add `POST /summary` endpoint
- `backend/app/schemas/ai_search.py`: add `SummaryRequest`, `SummaryResponse`; add `search_request_id: Optional[str] = None` to `AiSearchResult`
- `frontend/types/ai-search.ts`: update `ai_summary` (stays `string`) and add `search_request_id?: string`
- `frontend/lib/api/search.ts`: add `fetchSearchSummary(search_request_id)` function
- `backend/tests/test_f28_latency.py`: tests for summary endpoint happy path and unknown-ID 404

### T05 — Non-regression
- Read-only: runs `bash tools/run_eval.sh` and F27 pytest suite; documents pass/fail

### T06 — Review
- Reviews all implementation artifacts against acceptance criteria

### Forbidden for Codex
- Do NOT modify `frontend/app/`, `frontend/components/` (Gemini owns UI)
- Do NOT modify `frontend/types/ai-search.ts` in T01/T02 (only T03)
- Do NOT modify `backend/tests/eval_set.json`, `test_eval.py`, `eval_set_f27.json`, `test_eval_f27.py`
- Do NOT modify `status.json`

---

## Gemini (T04)

### T04 — Deferred summary UI
- `frontend/app/(dashboard)/search/page.tsx`: add deferred summary fetch logic (use `fetchSearchSummary` from `lib/api/search.ts`)
- `frontend/components/features/search/`: create/modify components for summary placeholder and loaded state

### Forbidden for Gemini
- Do NOT modify `frontend/lib/api/` (Codex owns)
- Do NOT modify `frontend/types/` (Codex owns)
- Do NOT modify any backend files
- Do NOT modify `status.json`
