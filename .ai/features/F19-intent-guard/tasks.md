# F19 Tasks

## T01 — Codex: implement intent guard

**Owner:** codex
**Type:** build
**Depends on:** —

**Scope:**
- `backend/app/services/ai_search/service.py`

**Done condition:**
- `_is_property_search(query: str) -> bool` implemented with keyword heuristics + LLM fallback
- `ai_search()` calls `_is_property_search` before `_parse_filters`
- Non-search path returns early with `items=[]`, `total=0`, redirect `ai_summary`
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
