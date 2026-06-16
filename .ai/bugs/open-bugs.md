# Open Bug Registry

**Last updated:** 2026-06-15  
**Source run:** [post-F9 smoke results](./../qa-runs/2026-05-18-post-F9-smoke/results.md)  
**Scope:** Current open / deferred / skipped items only. Fixed BUG-001~009 not listed.

---

## Lifecycle Rules

- `open-bugs.md` only tracks current unresolved items: `open`, `in_progress`, `blocked`, `deferred`, and intentional `skipped` test gaps.
- Do not add fixed/closed historical bugs here; keep their detailed evidence in the originating QA run or feature artifact.
- When an item is fixed and verified, move it out of `open-bugs.md` to `.ai/bugs/closed-bugs.md` with:
  - fixed date
  - verifying test / QA result
  - fixing commit or feature/batch
  - link to original evidence
- Keep entries short. Use links to QA results/fix reports for detail.
- New QA runs or features should add unresolved follow-ups here during closure.

---

## Functional Bugs

### BUG-022 — Intent guard non-deterministic for compound queries

- **Status:** open
- **Severity:** P2 / High
- **Feature:** F19 / intent guard
- **Symptom:** Compound queries like "近地铁 四房" or "新楼 三房 港岛" sometimes return the non-search redirect ("不是房源筛选") instead of entering the search pipeline. Single-term queries work (BUG-020 fixed). Compound queries are non-deterministic.
- **Root cause:** `_PROPERTY_SEARCH_PATTERNS` line 62 uses `^...$` anchors, so F23 vocabulary terms (近地铁, 新楼, etc.) only match when they are the entire query. In a compound query the full string doesn't equal the term, so the pattern misses, and the query falls to the LLM fallback which is non-deterministic.
- **Fix direction:** Remove `^...$` anchors from line 62 of `_PROPERTY_SEARCH_PATTERNS` so vocabulary terms match as substrings. Do NOT modify `_is_property_search` function body.
- **File:** `backend/app/services/ai_search/service.py`







## Skipped Tests


## Backlog / Observations


