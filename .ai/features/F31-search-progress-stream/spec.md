# F31 — Search Progress Stream

## Goal

Eliminate blank waiting periods in AI search by emitting fine-grained progress
events at every real backend stage. Users should always see something changing
on screen — no silent gaps longer than the duration of a single backend step.

## Problem

F29 added SSE streaming but still has three silent gaps:

| Gap | Duration | Cause |
|-----|----------|-------|
| `started` → `parsed` | ~3–5 s | `_parse_filters` LLM call, no interim signal |
| `parsed` → `results` | ~3–5 s | `_resolve_result_ids` + unnecessary wait for `_interpret_needs` (results event doesn't carry interpreted_needs) |
| `results` → `summary` | ~3–5 s | `_generate_summary` LLM call; spinner exists but fires only after results render |

## Solution

### New SSE events

Add two new progress events and surface the existing `searching` event in the
frontend. Full property-search sequence becomes:

```
started        → (immediate)
parsing        → "理解搜索语义中..."      ← NEW, emitted before _parse_filters
parsed         → filters card renders
searching      → "检索匹配房源中..."      ← already emitted; frontend now surfaces it
results        → property cards render
summarizing    → "生成摘要中..."          ← NEW, emitted before _generate_summary
summary        → AI text renders
done
```

### Backend optimizations in the same pass

1. **Semantic prefetch**: start `embed_text(query) + semantic_search(embedding)` in
   a background thread in parallel with `_parse_filters`. By the time parsing
   finishes, the vector search is likely already done; `_resolve_result_ids`
   only needs to run the deterministic filter + merge (fast).

2. **Remove unnecessary `_interpret_needs` wait**: `_build_results_event_data`
   does not include `interpreted_needs`. The streaming path must not block on
   `interpret_needs_future.result()` before emitting `results`. Remove
   `_interpret_needs` from the streaming executor entirely (it is unused in the
   stream).

### New event payloads

```json
// parsing
{ "message": "理解搜索语义中..." }

// summarizing
{ "message": "生成摘要中..." }
```

`searching` payload is unchanged: `{ "stage": "searching", "message": "检索匹配房源中..." }`.

## Non-goals

- No fake progress bars or timers
- No changes to POST endpoint behavior or response schema
- No changes to search ranking, relaxation policy, or filter semantics
- No new pip packages
- `interpreted_needs` is only removed from the streaming executor; the POST
  endpoint's `ai_search()` is not changed
