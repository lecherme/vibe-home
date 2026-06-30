# F31 Tasks

## T01 — Backend: new events + executor restructure

**Owner**: codex
**Type**: build
**Depends on**: —

Files in scope:
- `backend/app/schemas/ai_search.py`
- `backend/app/services/ai_search/service.py`
- `backend/tests/test_f31_stream.py` (new file)

What to do:

1. **New schemas** in `ai_search.py`:
   - `AiSearchParsingEventData(BaseModel)` with `message: str = "理解搜索语义中..."`
   - `AiSearchSummarizingEventData(BaseModel)` with `message: str = "生成摘要中..."`

2. **Restructure `ai_search_stream()`** in `service.py`:
   - Emit `("parsing", AiSearchParsingEventData())` immediately after `yield ("started", ...)`,
     before any LLM call
   - Start semantic prefetch in a background thread in parallel with `_parse_filters`:
     extract a `_run_semantic_prefetch(query)` helper that calls `embed_text` then
     `semantic_search`; submit it to a `ThreadPoolExecutor` before calling `_parse_filters`
   - Call `_parse_filters` (blocks), then yield `parsed`
   - Retrieve semantic prefetch result; pass `query_embedding` and `semantic_ids` into
     `_resolve_result_ids` so it skips `embed_text + semantic_search`
   - **Remove `_run_interpret_needs` from the executor entirely** — `_interpret_needs`
     is not needed anywhere in the streaming path; do not await it before `results`
   - Emit `("summarizing", AiSearchSummarizingEventData())` immediately after
     `yield ("results", ...)`, before calling `_generate_summary`
   - The `searching` event is already emitted between `parsed` and the executor phase;
     update its message to "检索匹配房源中..."

3. **Tests** in `test_f31_stream.py`:
   - Test that event sequence is `started → parsing → parsed → searching → results → summarizing → summary → done`
   - Test that `parsing` is emitted before `_parse_filters` is called
   - Test that `summarizing` is emitted before `_generate_summary` is called
   - Test that `results` is emitted without waiting for any `_interpret_needs` call

Done condition: the eight-event sequence is enforced by tests, and `bash tools/run_eval.sh` passes.

---

## T02 — Frontend: types + API callbacks

**Owner**: codex
**Type**: build
**Depends on**: T01

Files in scope:
- `frontend/types/ai-search.ts`
- `frontend/lib/api/ai-search.ts`

What to do:

1. **New types** in `ai-search.ts`:
   - `AiSearchParsingEventData { message: string }`
   - `AiSearchSummarizingEventData { message: string }`
   - `AiSearchParsingEvent { event: "parsing"; data: AiSearchParsingEventData }`
   - `AiSearchSummarizingEvent { event: "summarizing"; data: AiSearchSummarizingEventData }`
   - Add both to `AiSearchStreamEvent` union

2. **Callbacks** in `ai-search.ts`:
   - Add `onParsing?: (data: AiSearchParsingEventData) => void` to `AiSearchStreamCallbacks`
   - Add `onSummarizing?: (data: AiSearchSummarizingEventData) => void` to `AiSearchStreamCallbacks`
   - Wire both into `dispatchStreamEvent`
   - `onSearching` callback already exists; no change needed

Done condition: all new types exported, callbacks wired, no TypeScript errors.

---

## T03 — Frontend UI: progress stage display

**Owner**: codex
**Type**: build
**Depends on**: T02

Files in scope:
- `frontend/app/(dashboard)/search/page.tsx`

What to do:

Add a `aiStageMessage` state (`string | null`) to `SearchContent`. Drive it with the new callbacks:

- `onParsing` → set `aiStageMessage` to the parsing message
- `onSearching` → set `aiStageMessage` to the searching message
- `onResults` → set `aiStageMessage` to null (results replace the progress line)
- `onSummarizing` → set `aiStageMessage` to the summarizing message
- `onSummary` → set `aiStageMessage` to null
- `onDone` / `onError` → set `aiStageMessage` to null

In the AI mode rendering area (below `AiSearchBar`, above `AiParsedFiltersCard` when `aiParsedResult` is null; or below `InterpretedNeedsCard` when parsed is available), render a progress line:

```tsx
{aiLoading && aiStageMessage && (
  <div className="mt-3 flex items-center gap-2 text-sm text-gray-500">
    <div className="h-3 w-3 animate-spin rounded-full border-2 border-gray-300 border-t-gray-600" />
    <span>{aiStageMessage}</span>
  </div>
)}
```

Clear `aiStageMessage` (set to null) when a new search starts (inside `performAiSearch` init block).

Done condition: user sees "理解搜索语义中..." immediately on search submit; sees "检索匹配房源中..." after filters card appears; sees "生成摘要中..." after property cards render; no stage message visible after summary text arrives.

---

## T04 — Codex review

**Owner**: codex
**Type**: review
**Depends on**: T01, T02, T03

---

## T05 — Claude acceptance

**Owner**: claude
**Type**: acceptance
**Depends on**: T04
