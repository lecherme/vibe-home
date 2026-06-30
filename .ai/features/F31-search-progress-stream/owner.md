# F31 Owner Map

## Task ownership

| Task | Owner | Type |
|------|-------|------|
| T01 | codex | build |
| T02 | codex | build |
| T03 | codex | build |
| T04 | codex | review |
| T05 | claude | acceptance |

## File boundaries

### T01 — Backend only
- `backend/app/schemas/ai_search.py`
- `backend/app/services/ai_search/service.py`
- `backend/tests/test_f31_stream.py`

Forbidden:
- Any file under `frontend/`
- `.ai/**/status.json`
- `backend/requirements.txt`

### T02 — Frontend types + API wrapper only
- `frontend/types/ai-search.ts`
- `frontend/lib/api/ai-search.ts`

Forbidden:
- Any backend file
- `frontend/app/` (pages)
- `frontend/components/`
- `.ai/**/status.json`

### T03 — Frontend UI only
- `frontend/app/(dashboard)/search/page.tsx`

Forbidden:
- Any backend file
- `frontend/types/`
- `frontend/lib/api/`
- `.ai/**/status.json`

## Global constraints

- No worker may modify `.ai/**/status.json`
- No new pip packages (`backend/requirements.txt` must not change)
- No changes to POST `/api/v1/search/ai` contract
- No fake progress (timers, synthetic delays, progress bars not tied to real events)
