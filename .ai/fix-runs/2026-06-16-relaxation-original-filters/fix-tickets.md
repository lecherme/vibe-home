# Fix Tickets — 2026-06-16 Relaxation original filters

Standalone fix for BUG-025: parsed_filters should preserve original filters when relaxation occurs.
Source: `.ai/bugs/open-bugs.md`

---

## BUG-025-FIX

- **Bug:** BUG-025 — parsed_filters should preserve original filters when relaxation occurs
- **Owner:** Codex
- **Severity:** P2 / High
- **Allowed files:**
  1. `backend/app/services/ai_search/service.py`
- **Requirements:**
  1. In `ai_search()`, save a copy of `parsed_filters` (the original parsed user intent) before any call to `_apply_relaxation`
  2. When relaxation is triggered (the `strict_count == 0` branch that currently reassigns `parsed_filters` on line ~815), capture the relaxed filters into a separate local variable — do NOT overwrite the original `parsed_filters`
  3. The `AiSearchResult` at the end of `ai_search()` must set `parsed_filters` to the original (pre-relaxation) value
  4. `_generate_summary` call must still receive `relaxed_conditions` so it can describe what was relaxed
  5. Do NOT modify `_apply_relaxation`, `_relax_filters`, `_generate_summary`, `_is_property_search`, `_resolve_result_ids`, or `_parse_filters`
  6. Do NOT modify any other file
  7. `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exits 0
- **Verification:** `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exit 0
- **Status:** pending
