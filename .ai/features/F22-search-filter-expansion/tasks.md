# F22 Tasks

## T01 — Codex: implement search filter expansion

**Owner:** codex
**Type:** build
**Depends on:** —

**Scope:**
- `backend/app/schemas/search.py`
- `backend/app/services/search/service.py`
- `backend/app/services/ai_search/service.py`
- `frontend/types/search.ts`

**Done condition:**
- `SearchFilters` exposes `area_min`, `area_max`, `built_year_min`, `subway_distance_max` as optional integer fields
- `search()` applies each new filter when set, using the corresponding `area_sqm`, `built_year`, `subway_distance_m` property fields
- `_parse_filters` extracts the new fields from explicit numeric expressions as specified in `spec.md`; `current_year` uses server UTC year at parse time
- `_normalize_filters` and `_has_filters` updated to include new fields
- Frontend `SearchFilters` interface declares matching optional fields
- `_relax_filters` and `_apply_relaxation` are unchanged
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
