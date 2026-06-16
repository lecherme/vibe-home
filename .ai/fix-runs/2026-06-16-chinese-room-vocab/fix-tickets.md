# Fix Tickets — 2026-06-16 Chinese room vocabulary

Standalone fix for BUG-023: 中文数字房间词不解析为 bedrooms_min。
Source: `.ai/bugs/open-bugs.md`

---

## BUG-023-FIX

- **Bug:** BUG-023 — 中文数字房间词不解析为 bedrooms_min
- **Owner:** Codex
- **Severity:** P2 / High
- **Allowed files:**
  1. `backend/app/services/ai_search/service.py`
- **Requirements:**
  1. Inside `_normalize_query()`, in the "bedroom bare counts" block (the group of `_extract_bare_count` calls that handle `\d+室`, `\d+卧`, `\d+bedrooms?`), add one more `_extract_bare_count` call for `\d+房`, with a negative lookahead that excludes ambiguous following characters: 源、子、价、间、龄、东
  2. Do NOT modify any other function. Protected: `_is_property_search`, `_parse_filters`, `_relax_filters`, `_apply_relaxation`, `_resolve_result_ids`, `_generate_summary`
  3. Do NOT modify any other file
  4. After the fix: `_parse_filters("四房")` yields `bedrooms_min == 4`, and `_parse_filters("三房")` yields `bedrooms_min == 3`
  5. `bash tools/run_eval.sh` must pass
  6. `docker compose exec -T backend python3 -c "import app.main; print('OK')"` exits 0
- **Verification:** `bash tools/run_eval.sh` exit 0
- **Status:** pending
