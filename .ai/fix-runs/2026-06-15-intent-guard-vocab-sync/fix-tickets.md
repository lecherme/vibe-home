# Fix Tickets — 2026-06-15 intent guard vocabulary sync

Standalone fix for BUG-020: F23 bare vocabulary queries blocked by F19 intent guard.
Source: `.ai/bugs/open-bugs.md`

---

## BUG-020-FIX

- **Bug:** BUG-020 — F23 bare vocabulary queries blocked by F19 intent guard
- **Owner:** Codex
- **Severity:** P2 / High
- **Allowed files:**
  1. `backend/app/services/ai_search/service.py`
- **Requirements:**
  1. Add one new `re.compile(...)` entry to `_PROPERTY_SEARCH_PATTERNS` (the module-level tuple at the top of the file, around line 43) that matches all nine F23 vocabulary terms: `新楼`, `次新楼`, `次新房`, `较新`, `新建`, `近地铁`, `靠近地铁`, `地铁口`, `步行到地铁`
  2. Do NOT modify the `_is_property_search` function body
  3. Do NOT modify any existing entry in `_PROPERTY_SEARCH_PATTERNS` or `_NON_SEARCH_PATTERNS`
  4. Do NOT modify any other function or module-level symbol
  5. `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exits 0
- **Verification:** `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exit 0
- **Status:** pending
