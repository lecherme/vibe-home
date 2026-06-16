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

### BUG-025 — parsed_filters should preserve original filters when relaxation occurs

- **Status:** open
- **Severity:** P2 / High
- **Feature:** F20 / ai_search()
- **Symptom:** When a query like "四房 2000w预算 近地铁" triggers relaxation (strict results = 0), the API response field `parsed_filters` reflects the relaxed filters (e.g., bedrooms_min=3) instead of the original parsed intent (bedrooms_min=4). Frontend UNDERSTOOD FILTERS chip shows wrong value.
- **Root cause:** `ai_search()` line 815: `result_ids, parsed_filters, relaxed_conditions = _apply_relaxation(...)` overwrites `parsed_filters`; line 872 then returns the relaxed value.
- **Fix direction:** Save original `parsed_filters` before any `_apply_relaxation` call; return original in `AiSearchResult.parsed_filters`.
- **File:** `backend/app/services/ai_search/service.py`






## Skipped Tests


## Backlog / Observations


