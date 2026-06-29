# F29 Owner Map

| Task | Owner | Type |
|------|-------|------|
| T01 | codex | build |
| T02 | codex | build |
| T03 | codex | build |
| T04 | codex | review |
| T05 | claude | acceptance |

## Per-task file boundaries

### T01 (Codex — backend streaming endpoint)

**Allowed:**
- `backend/app/services/ai_search/service.py`
- `backend/app/api/v1/ai_search/router.py`
- `backend/app/schemas/ai_search.py`
- `backend/tests/test_f29_stream.py`

**Forbidden:**
- Any file under `frontend/`
- Any existing test file (`test_eval_f26.py`, `test_eval_f27.py`, `test_f28_latency.py`)

### T02 (Codex — frontend types and API wrapper)

**Allowed:**
- `frontend/types/ai-search.ts`
- `frontend/lib/api/ai-search.ts`

**Forbidden:**
- Any file under `backend/`
- Any file under `frontend/app/` or `frontend/components/`

### T03 (Codex — frontend UI progressive rendering)

**Allowed:**
- `frontend/app/(dashboard)/search/page.tsx`
- `frontend/components/features/search/ai-search-results.tsx`

**Forbidden:**
- Any file under `backend/`
- `frontend/types/` or `frontend/lib/`

## Global constraints (all workers)

- Workers must not modify `status.json`
- Do not change search semantics, ranking rules, relaxation policy, or POST endpoint contract
- Internal refactoring of `ai_search()` is permitted only if required to support the streaming path and behavior parity is preserved
- Do not add any new pip packages; use FastAPI's built-in `StreamingResponse`

## Claude constraints (T05)

- Perform acceptance directly (do not run via run_task.sh)
- Write final-report.md before updating status.json
