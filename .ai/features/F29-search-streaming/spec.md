# F29 — Search Streaming (SSE)

## Goal

Add Server-Sent Events (SSE) streaming to AI search so users see progressive
feedback instead of a blank screen for ~11.6 seconds.

The existing `POST /api/v1/search/ai` endpoint is **not changed**. F29 adds
a new streaming endpoint alongside it.

## Problem

Current `ai_search()` blocks until all stages complete (~11.6s total):

| Stage | Duration | Can stream early? |
|-------|----------|-------------------|
| `_parse_filters` | ~2–3s (LLM) | After: emit `parsed` |
| `_interpret_needs` + `_resolve_result_ids` | ~3–5s (parallel) | — |
| relaxation + filter | ~1.5s | — |
| `_collect_items` | <100ms | After: emit `results` |
| `_generate_summary` | ~2–4s (LLM) | After: emit `summary` |

Users can see property cards ~7–8s in, saving 2–4s of blank wait.

## New endpoint

```
GET /api/v1/search/ai/stream
Query params: query (str), page (int, default 1), page_size (int, default 20)
Response: text/event-stream
Auth: Bearer token (same as POST endpoint)
```

## SSE event sequence

```
event: started
data: {}

event: parsed
data: { "query_parsed": bool, "parsed_filters": {...}, "parsed_constraints": [...],
        "interpreted_intent": [...], "interpreted_needs": {...} }

event: searching
data: { "stage": "searching", "message": "Searching properties..." }

event: results
data: { "items": [...], "strict_items": [...], "recommended_items": [...],
        "total": int, "page": int, "page_size": int,
        "relaxations": [...], "match_reasons": {...} }

event: summary
data: { "ai_summary": str }

event: done
data: {}
```

On error:
```
event: error
data: { "message": str }
```

## Frontend behaviour

- On `parsed`: show detected filter chips (AiParsedFiltersCard already exists)
- On `searching`: keep skeleton visible
- On `results`: render property cards; show summary spinner
- On `summary`: replace summary spinner with final AI summary text
- On `error`: show error state
- Summary section shows a loading indicator until `summary` event arrives

## Non-goals

- No change to search semantics, ranking rules, relaxation policy, or existing POST response contract
- Internal refactoring is allowed if needed to support staged streaming and preserve behavior parity
- No pagination for the streaming endpoint (page/page_size pass through as-is)
- No WebSocket — SSE is unidirectional and sufficient

## Dependencies

- F30 must be done (relaxation optimization already merged)
