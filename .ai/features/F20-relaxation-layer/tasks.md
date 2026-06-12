# F20 Tasks

## T01 — Codex: implement relaxation layer

**Owner:** codex
**Type:** build
**Depends on:** —

**Scope:**
- `backend/app/services/ai_search/service.py`

**Done condition:**
- `_RELAX_SUPPLEMENT_THRESHOLD` constant defined
- `_relax_filters` implemented: one step per call, returns `None` when exhausted, never touches hard constraints
- `_apply_relaxation` implemented: loops `_relax_filters`, calls `_resolve_result_ids` between steps, stops at threshold or max 3 steps
- `_generate_summary` accepts `relaxed_conditions: list[str]` parameter
- `ai_search()` triggers rescue path when `strict_count == 0` and supplement path when `0 < strict_count < _RELAX_SUPPLEMENT_THRESHOLD`, both gated on `query_parsed=True`
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
