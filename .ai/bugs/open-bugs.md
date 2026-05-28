# Open Bug Registry

**Last updated:** 2026-05-25  
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


## Skipped Tests


## Backlog / Observations

### BUG-018 — Admin properties table overlaps on tablet/narrow viewport
- **Severity:** P3 · Low
- **Status:** backlog
- **Source:** PAGINATION-UX-FIX 手测 2026-05-28
- **Summary:** `/admin/properties` 表格在 iPad / 窄屏下 property title、location 过长时各列重叠，体验差
- **Affected files:** `frontend/app/(dashboard)/admin/properties/page.tsx`
- **Suggested next action:** 单独分析窄屏布局，选方案（横向滚动 / truncate / 响应式隐藏列 / card layout）后开 fix ticket

---

