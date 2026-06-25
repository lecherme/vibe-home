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

## T03
**title**: Decouple `_generate_summary` — context store, summary endpoint, schema, frontend contract
**owner**: codex
**type**: build
**depends_on**: T02

**Scope**:
- `backend/app/services/ai_search/service.py`
- `backend/app/api/v1/ai_search/router.py`
- `backend/app/schemas/ai_search.py`
- `frontend/types/ai-search.ts`
- `frontend/lib/api/search.ts`
- `backend/tests/test_f28_latency.py`

**Done condition**:
`ai_search()` generates a UUID, stores `SummaryContext` in an in-process TTLCache (TTL 120 s, max 512), returns `ai_summary=""` and `search_request_id=<uuid>`. `POST /api/v1/search/ai/summary` accepts `{search_request_id}`, fetches context from the store, calls `_generate_summary`, returns `{ai_summary: str}`, and removes the entry. `AiSearchResult.ai_summary` remains `str` (empty string default — no API break). `search_request_id: Optional[str] = None` is added as a new additive field. `frontend/types/ai-search.ts` and `frontend/lib/api/search.ts` are updated to match. `npx tsc --noEmit` exits 0. Tests cover: summary endpoint happy path and unknown-ID 404.

**Verification**:
`cd frontend && npx tsc --noEmit`

---

## T04
**title**: Frontend — deferred summary UI
**owner**: gemini
**type**: build
**depends_on**: T03

**Scope**:
- `frontend/app/(dashboard)/search/page.tsx`
- `frontend/components/features/search/` (new or modified components only)

**Done condition**:
When `ai_summary === ""` and `search_request_id` is set, the search page shows a "Generating summary…" placeholder in the summary area. A secondary request to `POST /api/v1/search/ai/summary` fires after results render. The summary text replaces the placeholder on arrival. If the secondary request fails, the placeholder is silently removed. No changes to `frontend/lib/api/` or `frontend/types/`. `npx tsc --noEmit` exits 0.

**Verification**:
`cd frontend && npx tsc --noEmit`

---

## T05
**title**: Non-regression eval — F16 + F27
**owner**: codex
**type**: build
**depends_on**: T02, T03

**Scope**: (read-only — no source files modified)

**Done condition**:
`bash tools/run_eval.sh` exits 0 (F16 eval) and F27 eval `docker compose run --rm -v $(pwd)/backend/tests:/app/tests backend python3 -m pytest /app/tests/test_eval_f27.py -q` exits 0. Results documented in build report.

**Verification**:
`bash tools/run_eval.sh`

---

## T06
**title**: Codex review
**owner**: codex
**type**: review
**depends_on**: T01, T02, T03, T04, T05

---

## T07
**title**: Claude acceptance
**owner**: claude
**type**: acceptance
**depends_on**: T06
