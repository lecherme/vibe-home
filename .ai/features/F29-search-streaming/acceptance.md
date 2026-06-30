# F29 Acceptance Criteria

## Backend (T01)

| ID | Criterion |
|----|-----------|
| A1 | `GET /api/v1/search/ai/stream` returns `Content-Type: text/event-stream` |
| A2 | Events are emitted in order: `started` → `parsed` → `searching` → `results` → `summary` → `done` for property searches, with the following strict causality: `parsed` is yielded immediately after `_parse_filters` returns (before `_resolve_result_ids` or `_collect_items` starts or completes); `results` is yielded after `_collect_items` completes and **before** `_generate_summary` is called |
| A3 | `parsed` payload contains `query_parsed` (bool), `parsed_filters` (object), `parsed_constraints` (array), `interpreted_intent` (array), `interpreted_needs` (object) |
| A4 | `results` payload contains `items`, `strict_items`, `recommended_items`, `total`, `page`, `page_size`, `relaxations`, `match_reasons` |
| A5 | `summary` payload contains `ai_summary` (non-empty string) |
| A6 | Non-property-search queries complete successfully and surface the same non-search redirect behavior as the POST endpoint; stream may skip `parsed`/`searching`/`summary` but must emit a terminal results-compatible payload (with empty items and redirect message) before `done` |
| A7 | Error path emits `error` event with `message` field and closes the stream |
| A8 | Existing `POST /api/v1/search/ai` endpoint response contract is unchanged |
| A9 | `test_f29_stream.py` tests cover: event order, payload shapes, error path, non-search query path |
| A10 | `bash tools/run_eval.sh` passes (F16 non-regression) |

## Frontend types (T02)

| ID | Criterion |
|----|-----------|
| A11 | TypeScript types exist for each SSE event payload in `frontend/types/ai-search.ts` |
| A12 | `aiSearchStream()` in `frontend/lib/api/ai-search.ts` uses `fetch` + `ReadableStream` (not EventSource) |
| A13 | `aiSearchStream()` returns an `AbortController` (or cancellation function) |
| A14 | Existing `aiSearch()` function is unchanged |

## Frontend UI (T03)

| ID | Criterion |
|----|-----------|
| A15 | `AiParsedFiltersCard` appears as soon as the `parsed` event arrives (before `results`) |
| A16 | Property cards render upon `results` event, before `summary` arrives |
| A17 | Summary section shows a loading indicator between `results` and `summary` |
| A18 | Summary text is displayed once `summary` event arrives |
| A19 | Triggering a new search aborts any in-flight stream |
| A20 | `aiLoading` becomes false after `done` or `error` event |

---

## Review and Acceptance

- T04 (Codex review) verifies all criteria and writes `review.md`
- T05 (Claude acceptance) reads `review.md` and writes `final-report.md`
- If `review.md` verdict is FAIL, Claude must not proceed to acceptance — apply the appropriate fix path per orchestration.md before re-running review

---

## Rejection Conditions

Any of the following causes immediate rejection:

- Existing `POST /api/v1/search/ai` contract changed (response schema, status codes, or behavior)
- Streaming implementation breaks non-streaming AI search (regression in `aiSearch()`)
- SSE events emitted out of order, or `parsed` is delayed until after `_resolve_result_ids`/`_collect_items` completes
- `results` is not emitted before `_generate_summary` is called (fake streaming)
- Frontend shows property results only after `summary` arrives (defeat the purpose of streaming)
- Non-property-search query returns no terminal payload before `done`
- Any worker modifies `status.json`
- New pip packages added to `backend/requirements.txt`
