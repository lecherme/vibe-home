# Fix Tickets — 2026-06-16 Intent guard compound queries

Standalone fix for BUG-022: intent guard non-deterministic for compound queries.
Source: `.ai/bugs/open-bugs.md`

---

## BUG-022-FIX

- **Bug:** BUG-022 — Intent guard non-deterministic for compound queries
- **Owner:** Codex
- **Severity:** P2 / High
- **Allowed files:**
  1. `backend/app/services/ai_search/service.py`
- **Requirements:**
  1. In `_PROPERTY_SEARCH_PATTERNS` (module-level constant), find the pattern that uses `^...$` anchors to match F23 vocabulary terms (新楼, 次新楼, 次新房, 较新, 新建, 近地铁, 靠近地铁, 地铁口, 步行到地铁). Remove the `^` and `$` anchors so these terms match as substrings anywhere in a query, not only when the entire query equals the term.
  2. All nine vocabulary terms in that pattern must be preserved exactly as-is; do not add or remove terms.
  3. Do NOT modify the `_is_property_search` function body (lines implementing the function logic).
  4. Do NOT modify `_NON_SEARCH_PATTERNS`.
  5. Do NOT modify any other function or constant.
  6. Do NOT modify any other file.
  7. `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exits 0
- **Verification:** `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exit 0
- **Status:** pending
