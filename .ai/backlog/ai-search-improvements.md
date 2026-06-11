# AI Search — Improvement Backlog

Post-F18 planning notes. Items are ordered by priority; do not start an item until the previous is accepted. Do not open a feature ticket until ready to implement.

---

## Next — Intent Guard

Distinguish property-search queries from non-search queries before entering the search/relaxation pipeline.

- Classify query as `property_search` or `non_search`
- Non-search queries return a polite redirect message; skip all filter parsing and retrieval
- Implementation: keyword heuristics first, LLM fallback for ambiguous cases

**Why first:** Lowest implementation cost, highest perceived intelligence gain. Prevents nonsensical results for queries like "上海房价为什么涨".

---

## Next — Relaxation Layer

When strict filters return zero or too few results, progressively relax soft constraints.

- Hard filters (price ceiling, status, explicit numeric bounds) are never relaxed
- Soft constraints (bedrooms_min, location, bathrooms_min) relaxed in a defined order
- Each relaxation step is recorded so summary can explain what was loosened
- Relaxation triggers only on strict-match zero result, not as default scoring

**Why second:** Single highest-impact improvement to search experience. A single mis-parsed filter currently produces empty results with no recovery path.

---

## Later — Property Schema Expansion

Add the minimum fields needed to make semantic search and relaxation meaningful.

Fields to add in one pass:
- `area_sqm`
- `built_year`
- `subway_distance_m`
- `tags`

Defer orientation, floor, elevator, description to a later pass once these four are validated.

**Dependency:** Relaxation layer should be live first so it can immediately benefit from new fields.

---

## Later — LLM Middle Layer

Handle complex compositional expressions that deterministic parsing cannot cover reliably.

- LLM receives only the residual query text after deterministic passes
- Output is a controlled intermediate structure (typed dict), not free-form filter values
- Strict output schema validation; hallucinations on unknown fields are dropped, not forwarded
- Examples: "一家四口" → `{bedrooms_min: 3}`, "改善型" → `{area_min: 100}`

**Dependency:** Schema expansion defines what fields the LLM is allowed to output.

---

## Later — Semantic Mapping & Explainable Summary

Produce a human-readable explanation of why results were returned and what conditions were relaxed.

- Summary references matched fields, relaxed constraints, and schema-backed reasons
- Example: "没有完全匹配三房预算内房源，已放宽预算 10%，以下 4 套优先保留嘉定和三房条件"

**Dependency:** Requires relaxation layer (for relaxation records) and schema expansion (for richer fields). Low value without both in place.
