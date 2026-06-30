## Disposition: ACCEPTED

# F31 Acceptance Report

## Verdict
PASS

## Criteria Verification

| ID | Result | Verified By |
|----|--------|-------------|
| A1 | PASS | `parsing` yielded at line 1506, before `_parse_filters` at line 1544; `test_f31_stream.py:173` asserts `"call:_parse_filters" not in call_order` after advancing to `parsing` event |
| A2 | PASS | `AiSearchParsingEventData.message = "理解搜索语义中..."` (default) |
| A3 | PASS | `summarizing` yielded at line 1663, before `_generate_summary` at line 1666; `test_f31_stream.py:189` asserts `_generate_summary` not called until after `summarizing` event |
| A4 | PASS | `AiSearchSummarizingEventData.message = "生成摘要中..."` (default) |
| A5 | PASS | 8-event sequence enforced: `started → parsing → parsed → searching → results → summarizing → summary → done` |
| A6 | PASS | `_interpret_needs` removed from streaming executor entirely; patched as AssertionError in test — any accidental call fails the suite |
| A7 | PASS | `_run_semantic_prefetch` submitted before `_parse_filters` call (line 1540–1544); `query_embedding` and `semantic_ids` passed into `_resolve_result_ids` (line 1571–1577); test asserts kwargs presence |
| A8 | PASS | POST `/api/v1/search/ai` handler unchanged; `ai_search()` function unchanged |
| A9 | PASS | `test_f31_stream.py` covers 4 cases: sequence, parsing causality, summarizing causality, results without interpret_needs |
| A10 | PASS | `bash tools/run_eval.sh` → 2 passed; `test_f29_stream.py` + `test_f31_stream.py` → 8 passed |
| A11 | PASS | `AiSearchParsingEventData`, `AiSearchSummarizingEventData` exported from `frontend/types/ai-search.ts` |
| A12 | PASS | `AiSearchStreamEvent` union includes `AiSearchParsingEvent` and `AiSearchSummarizingEvent` |
| A13 | PASS | `AiSearchStreamCallbacks` has `onParsing` and `onSummarizing` optional callbacks |
| A14 | PASS | Both callbacks wired in `dispatchStreamEvent` (`ai-search.ts:140–154`) |
| A15 | PASS | `onParsing` → `setAiStageMessage` → spinner renders immediately under `AiSearchBar` before parsed data exists |
| A16 | PASS | State transitions: parsing → searching → null (results) → summarizing → null (summary) — exact per spec |
| A17 | PASS | `aiStageMessage` cleared on `summary`, `done`, and `error` |
| A18 | PASS | `performAiSearch` init block clears `aiStageMessage` before starting new stream |
| A19 | PASS | **No flicker risk**: SSE blocks dispatched synchronously; if `results` + `summarizing` batch into one read, React state batching preserves the final state as `aiStageMessage="生成摘要中..."` — the message remains visible. Both batched and unbatched paths produce correct UI. |
| A20 | PASS | **Double signal acceptable**: stage message (filter card area) and `isSummaryLoading` spinner (inside `AiSearchResults`) are spatially distinct — "overall stage" vs "summary panel loading". Mild redundancy, not confusing noise. |

## Test Run

```
docker compose run --rm -v ./backend/tests:/app/tests backend \
  python3 -m pytest /app/tests/test_f31_stream.py /app/tests/test_f29_stream.py -q
8 passed, 1 warning in 0.90s

bash tools/run_eval.sh
2 passed, 1 warning in 0.84s
```

## Notes

- T04 first attempt FAIL on status.json ownership misread; second run PASS (same pattern as F29/F30).
- `test_f29_stream.py` updated as direct_fixup to reflect the new 8-event sequence and `检索匹配房源中...` message; all 4 existing F29 tests continue to pass.
- Double loading signal (A20) is a known mild redundancy; acceptable given spatial separation. If desired, `isSummaryLoading` in `AiSearchResults` could be removed in a future cleanup now that `summarizing` event covers this stage.
