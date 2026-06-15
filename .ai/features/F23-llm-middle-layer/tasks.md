# F23 Tasks

## T01 — Codex: implement LLM middle layer

**Owner:** codex
**Type:** build
**Depends on:** —

**Scope:**
- `backend/app/services/ai_search/service.py`

**Done condition:**
- LLM system prompt in `_parse_filters` allows `subway_distance_max` and `built_year_min` as output keys
- `current_utc_year - 10` is computed by Python and injected as a concrete value into the prompt; LLM does not perform year arithmetic
- LLM-provided `subway_distance_max` is validated (50–5000) before merging
- LLM-provided `built_year_min` is validated (1900–current_utc_year+1) before merging
- Deterministic values take priority over LLM values for the same field
- `_relax_filters`, `_apply_relaxation`, `_is_property_search`, `_resolve_result_ids`, `_generate_summary` are unchanged
- `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exits 0

---

## T02 — Codex: review

**Owner:** codex
**Type:** review
**Depends on:** T01

---

## T03 — Claude: acceptance

**Owner:** claude
**Type:** acceptance
**Depends on:** T02
