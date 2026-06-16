# Fix Tickets — 2026-06-16 Relaxation fallback disclosure

Standalone fix for BUG-024: relaxation fallback summary 丢失放宽说明。
Source: `.ai/bugs/open-bugs.md`

---

## BUG-024-FIX

- **Bug:** BUG-024 — Relaxation fallback summary 丢失放宽说明
- **Owner:** Codex
- **Severity:** P2 / High
- **Allowed files:**
  1. `backend/app/services/ai_search/service.py`
- **Requirements:**
  1. In `ai_search()`, in the `except` block that handles `_generate_summary` failure (currently sets `ai_summary = f"Found {total} properties matching your search."`), change the fallback so that when `relaxed_conditions` is non-empty, the message includes a disclosure that results were broadened beyond the original filters
  2. When `relaxed_conditions` is empty, the existing fallback text is acceptable unchanged
  3. Do NOT modify `_generate_summary`, `_relax_filters`, `_apply_relaxation`, `_resolve_result_ids`, `_parse_filters`, or any other function
  4. Do NOT modify any other file
  5. `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exits 0
- **Verification:** `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exit 0
- **Status:** pending
