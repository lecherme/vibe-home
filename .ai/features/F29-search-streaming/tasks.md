# F29 Tasks

## T01 — Backend streaming endpoint

**Owner:** codex
**Type:** build
**Depends on:** —

**Scope:**
- `backend/app/services/ai_search/service.py`
- `backend/app/api/v1/ai_search/router.py`
- `backend/app/schemas/ai_search.py`
- `backend/tests/test_f29_stream.py`

**Done condition:**
- `GET /api/v1/search/ai/stream` returns `Content-Type: text/event-stream`
- The six event types (`started`, `parsed`, `searching`, `results`, `summary`, `done`) are emitted in order
- `parsed` event payload includes `query_parsed`, `parsed_filters`, `parsed_constraints`, `interpreted_intent`, `interpreted_needs`
- `results` event payload includes `items`, `strict_items`, `recommended_items`, `total`, `page`, `page_size`, `relaxations`, `match_reasons`
- `summary` event payload includes `ai_summary`
- Errors emit an `error` event with `message` field and close the stream
- Existing `POST /api/v1/search/ai` endpoint and its response contract are unchanged
- Unit tests in `test_f29_stream.py` cover: event order, payload shapes, error path, non-search query path

---

## T02 — Frontend types and API wrapper

**Owner:** codex
**Type:** build
**Depends on:** T01

**Scope:**
- `frontend/types/ai-search.ts`
- `frontend/lib/api/ai-search.ts`

**Done condition:**
- TypeScript types defined for each SSE event payload (`AiSearchStreamEvent` discriminated union or per-event types)
- `aiSearchStream(query, page, pageSize, callbacks)` function added to `lib/api/ai-search.ts`:
  - Uses `fetch` + `ReadableStream` to consume the SSE stream
  - Calls `callbacks.onParsed`, `callbacks.onSearching`, `callbacks.onResults`, `callbacks.onSummary`, `callbacks.onDone`, `callbacks.onError` at the appropriate events
  - Returns an `AbortController` so callers can cancel mid-stream
- Existing `aiSearch()` function is unchanged

---

## T03 — Frontend UI: progressive rendering

**Owner:** codex
**Type:** build
**Depends on:** T02

**Scope:**
- `frontend/app/(dashboard)/search/page.tsx`
- `frontend/components/features/search/ai-search-results.tsx`

**Done condition:**
- `search/page.tsx` calls `aiSearchStream` instead of `aiSearch` for AI mode
- Property cards are rendered as soon as the `results` event arrives (before `summary`)
- `AiParsedFiltersCard` is shown as soon as the `parsed` event arrives
- Summary section shows a loading indicator between `results` and `summary` events
- Summary is displayed once the `summary` event arrives
- Previous in-flight stream is aborted when a new search is triggered
- `aiLoading` is set to false after the `done` or `error` event

---

## T04 — Review

**Owner:** codex
**Type:** review
**Depends on:** T01, T02, T03

---

## T05 — Acceptance

**Owner:** claude
**Type:** acceptance
**Depends on:** T04
