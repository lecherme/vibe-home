# F31 Acceptance Criteria

## Backend (T01)

| ID | Criterion |
|----|-----------|
| A1 | `parsing` event is emitted immediately after `started`, before `_parse_filters` is called |
| A2 | `parsing` payload is `{ "message": "理解搜索语义中..." }` |
| A3 | `summarizing` event is emitted immediately after `results`, before `_generate_summary` is called |
| A4 | `summarizing` payload is `{ "message": "生成摘要中..." }` |
| A5 | Full property-search event sequence is `started → parsing → parsed → searching → results → summarizing → summary → done` |
| A6 | `results` is emitted without calling or waiting for `_interpret_needs` in the streaming path |
| A7 | Semantic prefetch (`embed_text + semantic_search`) starts in parallel with `_parse_filters`; `_resolve_result_ids` receives pre-computed `query_embedding` and `semantic_ids` |
| A8 | Existing POST endpoint response contract is unchanged |
| A9 | `test_f31_stream.py` covers: eight-event sequence, `parsing` before `_parse_filters`, `summarizing` before `_generate_summary`, `results` without `_interpret_needs` wait |
| A10 | `bash tools/run_eval.sh` passes (F16 non-regression) |

## Frontend types (T02)

| ID | Criterion |
|----|-----------|
| A11 | `AiSearchParsingEventData` and `AiSearchSummarizingEventData` types are exported from `frontend/types/ai-search.ts` |
| A12 | `AiSearchStreamEvent` union includes `AiSearchParsingEvent` and `AiSearchSummarizingEvent` |
| A13 | `AiSearchStreamCallbacks` has `onParsing` and `onSummarizing` optional callbacks |
| A14 | Both callbacks are wired in `dispatchStreamEvent` in `ai-search.ts` |

## Frontend UI (T03)

| ID | Criterion |
|----|-----------|
| A15 | A progress line with spinner appears immediately on search submit (driven by `onParsing`) |
| A16 | Progress message transitions correctly: "理解搜索语义中..." → "检索匹配房源中..." → (results appear) → "生成摘要中..." → (summary appears, message clears) |
| A17 | No progress message is visible after `summary` event or after `done`/`error` |
| A18 | Starting a new search clears the previous `aiStageMessage` immediately |
| A19 | **UX: results→summarizing flicker risk** — `onResults` sets `aiStageMessage` to `null`, then `onSummarizing` sets it to "生成摘要中...". Reviewer must explicitly assess: are these two callbacks likely to be dispatched in separate browser render frames (making "生成摘要中..." reliably visible), or can they batch into one frame (causing the message to never appear)? Document the finding and risk level. |
| A20 | **UX: double loading signal** — after `results` arrives, both the `aiStageMessage` "生成摘要中..." (in the filter card area) and the `isSummaryLoading` spinner inside `AiSearchResults` are visible simultaneously. Reviewer must explicitly assess whether this creates confusing redundant noise, or whether the two signals are spatially distinct enough to be acceptable. Document the finding. |

---

## Review and Acceptance

- T04 (Codex review) verifies all criteria and writes `review.md`
- T05 (Claude acceptance) reads `review.md` and writes `final-report.md`
- If `review.md` verdict is FAIL, apply the appropriate fix path before re-running review

---

## Rejection Conditions

Any of the following causes immediate rejection:

- POST endpoint behavior or response schema changed
- `parsing` or `summarizing` emitted after the stage they precede (fake progress)
- `results` waits for `_interpret_needs` before emitting
- `_interpret_needs` called in the streaming executor (it must be removed)
- Progress message visible on screen after `summary` arrives
- New pip packages added to `backend/requirements.txt`
- Any worker modifies `status.json`
