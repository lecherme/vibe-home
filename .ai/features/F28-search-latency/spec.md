# F28 — Search Latency Pass

## Goal
Reduce AI search wall-clock latency by eliminating the two largest architectural bottlenecks:
1. Serial execution of two independent calls after `_parse_filters` completes
2. `_generate_summary` blocking result delivery

## Current bottleneck map

```
_parse_filters        (LLM #1,  ~3–8 s, always)
  ↓ serial
_interpret_needs      (LLM #2,  ~3–8 s, always)
  ↓ serial
_resolve_result_ids   (embedding + Supabase, ~5–15 s)
  ↓ serial
_generate_summary     (LLM #3/4, ~3–8 s, always)   ← blocks result delivery
```

## Phase 1 scope (this feature)

### 1. Instrumentation
Add `time.perf_counter()` timing around each stage in `ai_search()`, emitted as a single structured `logger.info` entry at the end:

Fields: `parse_filters_ms`, `interpret_needs_ms`, `resolve_ids_ms`, `collect_items_ms`, `total_ms`, `query`

Goal: establish real baseline before claiming optimization worked.

### 2. Parallelize `_interpret_needs` + `_resolve_result_ids`

After `_parse_filters` completes, these two are independent:
- `_interpret_needs(query, parsed_filters)` — LLM call
- `_resolve_result_ids(query, parsed_filters, query_parsed)` — embedding + vector search

Use `concurrent.futures.ThreadPoolExecutor` to run both concurrently inside the sync `ai_search()`.
Combined wall time = max(interpret_needs_time, resolve_ids_time), not their sum (~5–15 s saved).

Failure isolation: `_interpret_needs` exception must fall through to the existing empty-default path without affecting `_resolve_result_ids`.

### 3. Decouple `_generate_summary` from main response path

The summary is not a prerequisite for showing the user property results.

**Design — server-owned context store:**
- `ai_search()` generates a `search_request_id` (UUIDv4)
- Stores `SummaryContext(query, parsed_filters, total, items[:5], relaxed_conditions)` in a process-level `TTLCache` keyed by that ID (TTL 120 s, max 512 entries)
- Does NOT call `_generate_summary` in the main path
- Returns `AiSearchResult` with `ai_summary = ""` and `search_request_id = <uuid>`

Client calls `POST /api/v1/search/ai/summary` with body `{search_request_id}`:
- Server looks up context from the TTL store (no client-supplied items or filters)
- Calls `_generate_summary` using stored context
- Returns `{ai_summary: str}`
- Deletes the context entry after serving it (one-shot)

**Compatibility strategy:**
- `ai_summary: str = ""` — stays `str`, empty string when deferred (no breaking change; existing clients see `""` instead of a generated sentence)
- `search_request_id: Optional[str] = None` — new additive field; old clients ignore it
- Frontend: when `ai_summary == ""` and `search_request_id` is set, show "Generating summary…" and fire the secondary request

**No client-supplied context.** The summary endpoint receives only the opaque ID. The server is the sole source of truth for what was actually searched.

## Non-goals
- SSE / streaming (F29)
- In-memory query result cache (F28.1 or follow-up)
- Infrastructure / region changes
- Parallelizing `_apply_relaxation` (conditional, depends on strict_count)
- Changing filter, relaxation, or pagination logic

## Dependencies
- F27 done ✓
- F16 eval 30/30 must remain unchanged
- F27 eval 28/28 must remain unchanged
