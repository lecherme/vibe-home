# F28 — Search Latency Pass

## Goal
Reduce AI search wall-clock latency by eliminating the largest architectural bottleneck: serial execution of two independent operations after `_parse_filters` completes. Instrument each stage first to establish a real baseline.

## Current bottleneck map

```
_parse_filters        (LLM #1,  ~3–8 s, always)
  ↓ serial
_interpret_needs      (LLM #2,  ~3–8 s, always)
  ↓ serial
_resolve_result_ids   (embedding + Supabase, ~5–15 s)
  ↓ serial
_generate_summary     (LLM #3/4, ~3–8 s, always)
```

## Changes in scope

### 1. Instrumentation
Add `time.perf_counter()` timing around each stage in `ai_search()`, emitted as a single structured `logger.info` entry at function end:

Fields: `parse_filters_ms`, `interpret_needs_ms`, `resolve_ids_ms`, `collect_items_ms`, `total_ms`, `query`

Goal: establish real baseline. Do not guess, measure.

### 2. Parallelize `_interpret_needs` + `_resolve_result_ids`

After `_parse_filters` completes, these two are independent:
- `_interpret_needs(query, parsed_filters)` — LLM call
- `_resolve_result_ids(query, parsed_filters, query_parsed)` — embedding + vector search

Use `concurrent.futures.ThreadPoolExecutor` to run both concurrently inside the sync `ai_search()`.
Combined wall time = max(interpret_needs_time, resolve_ids_time), not their sum (~5–15 s saved).

Failure isolation: `_interpret_needs` exception must fall through to the empty-default path without affecting `_resolve_result_ids`.

## Non-goals
- SSE / streaming (F29)
- Summary decoupling / deferred `_generate_summary` (deferred to F29 — requires proper streaming API contract)
- In-memory query result cache (F28.1 or follow-up)
- Infrastructure / region changes
- Parallelizing `_apply_relaxation` (conditional, depends on strict_count)
- Changing filter, relaxation, or pagination logic
- Any frontend changes

## Dependencies
- F27 done ✓
- F16 eval 30/30 must remain unchanged
- F27 eval 28/28 must remain unchanged
