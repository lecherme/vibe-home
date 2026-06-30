# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | `parsing` is yielded immediately after `started` and before `_parse_filters` in `backend/app/services/ai_search/service.py:1505-1506,1543-1545`; test coverage in `backend/tests/test_f31_stream.py:173-186`. |
| A2 | PASS | `AiSearchParsingEventData.message` defaults to `"理解搜索语义中..."` in `backend/app/schemas/ai_search.py:86-87`. |
| A3 | PASS | `summarizing` is yielded immediately after `results` and before `_generate_summary` in `backend/app/services/ai_search/service.py:1662-1666`; test coverage in `backend/tests/test_f31_stream.py:189-209`. |
| A4 | PASS | `AiSearchSummarizingEventData.message` defaults to `"生成摘要中..."` in `backend/app/schemas/ai_search.py:106-107`. |
| A5 | PASS | The stream test enforces `started -> parsing -> parsed -> searching -> results -> summarizing -> summary -> done` in `backend/tests/test_f31_stream.py:152-170`. |
| A6 | PASS | The streaming path no longer submits or awaits `_interpret_needs`; `ai_search_stream()` uses only semantic prefetch, and the test asserts no `_interpret_needs` call before `results` in `backend/tests/test_f31_stream.py:212-220`. |
| A7 | PASS | Semantic prefetch is submitted before `_parse_filters` (`service.py:1540-1545`), then `query_embedding` and `semantic_ids` are passed into `_resolve_result_ids` (`service.py:1570-1577`); `_resolve_result_ids` honors precomputed values in `service.py:1231-1272`. |
| A8 | PASS | The POST route still returns `AiSearchResult` via `ai_search()` in `backend/app/api/v1/ai_search/router.py:19-24`; the non-stream `ai_search()` path still owns `interpreted_needs` and response assembly in `backend/app/services/ai_search/service.py:1287-1498`. |
| A9 | PASS | `backend/tests/test_f31_stream.py` covers sequence, `parsing` ordering, `summarizing` ordering, and no `_interpret_needs` wait. |
| A10 | PASS | `bash tools/run_eval.sh` exited `0` locally during review. |
| A11 | PASS | `AiSearchParsingEventData` and `AiSearchSummarizingEventData` are exported from `frontend/types/ai-search.ts:81-103`. |
| A12 | PASS | `AiSearchStreamEvent` includes both new event types in `frontend/types/ai-search.ts:154-162`. |
| A13 | PASS | `AiSearchStreamCallbacks` includes `onParsing` and `onSummarizing` in `frontend/lib/api/ai-search.ts:90-100`. |
| A14 | PASS | Both callbacks are dispatched in `frontend/lib/api/ai-search.ts:136-166`. |
| A15 | PASS | The progress line is driven by `onParsing` (`frontend/app/(dashboard)/search/page.tsx:181-184`) and rendered above parsed filters when no parsed result exists (`page.tsx:323-329`). |
| A16 | PASS | Stage transitions are wired as specified: parsing (`page.tsx:181-184`), searching (`190-193`), clear on results (`194-205`), summarizing (`219-222`), clear on summary (`207-217`). |
| A17 | PASS | `aiStageMessage` is cleared on `summary`, `done`, and `error` in `frontend/app/(dashboard)/search/page.tsx:207-235`. |
| A18 | PASS | A new search clears the prior stage message immediately in the init block at `frontend/app/(dashboard)/search/page.tsx:167-171`. |
| A19 | PASS | `results` and `summarizing` can batch in one `reader.read()` turn because SSE blocks are drained synchronously in `frontend/lib/api/ai-search.ts:211-229`. That is low risk here: the batched final state still has `aiResult` set and `aiStageMessage="生成摘要中..."`, so the summarizing line remains visible in `page.tsx:194-222,342-347`. |
| A20 | PASS | There are two simultaneous loading signals during summary generation: the stage line in `frontend/app/(dashboard)/search/page.tsx:342-347` and the in-card spinner in `frontend/components/features/search/ai-search-results.tsx:52-63`. This is mildly redundant but spatially distinct enough to be acceptable. |
| Frontend business logic stays out of components | PASS | `frontend/app/(dashboard)/search/page.tsx` only orchestrates UI state and stream callbacks; parsing, ranking, relaxation, and summary generation remain in backend services. |
| `status.json` was not modified by Codex or Gemini | PASS | No evidence points to Codex/Gemini as the author of the current `status.json` change; the activity log attributes the T04 update to `claude` in `.ai/features/F31-search-progress-stream/status.json:116-120`. |
| Global constraint: no worker modifies `.ai/**/status.json` | FAIL | `.ai/features/F31-search-progress-stream/status.json` is modified in the working tree, and the file records a worker-written T04 update (`current_stage/current_owner/task status/activity_log`) in `.ai/features/F31-search-progress-stream/status.json:4-6,43-55,116-120`. This is an explicit rejection condition. |

## Issues Found
- BLOCKER: `.ai/features/F31-search-progress-stream/status.json` was modified during the task flow. The current diff shows T04 state changes in that file, and the activity log attributes the write to `claude`. The spec’s rejection conditions forbid any worker from modifying `status.json`.
- WARNING: The summary phase shows two concurrent loading indicators: the stage line above the cards and the spinner inside `AiSearchResults`. It is acceptable, but slightly noisier than necessary.

## Required Fixes
- Revert the `.ai/features/F31-search-progress-stream/status.json` working tree change and prevent the task orchestration flow from writing that file during Codex/Claude execution.

## Approved Items
- Backend stream sequencing, new event payloads, semantic prefetch, and removal of streaming `_interpret_needs` are correctly implemented.
- The POST `/api/v1/search/ai` contract remains unchanged.
- Frontend API types and callbacks for `parsing` and `summarizing` are published and wired correctly.
- The page-level progress message lifecycle matches the intended stage transitions and clears correctly on new search, summary, done, and error.
- `bash tools/run_eval.sh` passed, and frontend TypeScript checked cleanly with `./node_modules/.bin/tsc --noEmit`.
