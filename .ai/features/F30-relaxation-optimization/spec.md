# F30 — Relaxation Optimization

## Problem

F28 timing log revealed `relaxation_ms = 35s` out of `total_ms = 44s`. The relaxation
path currently:

1. Iterates `strict_result_ids` one-by-one calling `get_by_id()` + filter checks
2. Calls `_apply_relaxation()`, which internally calls `_resolve_result_ids()` for
   each relaxation step — repeating `embed_text(query)` + `semantic_search()` on the
   same query that was already embedded at the start of `ai_search()`
3. Iterates `relaxed_result_ids` one-by-one calling `get_by_id()` + filter checks

This means 2–N redundant embedding + vector search calls per search, each costing
~1–3s, stacking inside relaxation.

## Goal

Reduce `relaxation_ms` materially from the F28 baseline (~35000 ms) by:

1. **Embedding reuse** — compute `embed_text(query)` once before relaxation; pass it
   into `_resolve_result_ids` and `_apply_relaxation` so it is never recomputed
2. **Semantic result reuse** — the initial `_resolve_result_ids()` call already has the
   ranked semantic IDs; `_apply_relaxation()` must reuse those IDs and only vary the
   filter combination, not re-run the vector search
3. **Batch property fetch** — replace the per-ID `get_by_id()` loop in both strict and
   relaxed filtering with a single batch fetch call, eliminating N round-trips

## Non-goals

- SSE / streaming (F29)
- Summary decoupling (F29)
- Any frontend, API schema, or Supabase schema changes
- Cross-request embedding cache (deferred)

## Required observable outcomes

After this feature:
- `relaxation_ms` is materially reduced from the F28 baseline (~35000 ms)
- For parsed property searches with non-empty query, `embed_text(query)` is called
  at most once per `ai_search()` invocation
- For parsed property searches with non-empty query, `semantic_search()` is called
  at most once per `ai_search()` invocation; relaxation steps must not trigger
  additional embedding or semantic search calls
- Timing log includes `strict_filtering_ms`, `apply_relaxation_ms`,
  `relaxed_filtering_ms`, `relaxation_steps` for post-optimization diagnosis
- F16 + F27 non-regression evals continue to pass

## Dependencies

- F27: done
- F28: done (timing instrumentation already in place)
