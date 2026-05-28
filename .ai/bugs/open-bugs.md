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


### BUG-017 / PAGINATION-UX — 全部列表页分页缺少直接跳页能力
- **Severity:** P3 · Low
- **Status:** in_progress — PAGINATION-UX-FIX ticket 已创建
- **Source:** BUG-011-FIX 复测 2026-05-25
- **Summary:** /properties、/search、/favorites、/admin/properties 均只有 Previous/Next；扩展为抽 PaginationControls 共享组件 + 加 Go-to-page 跳页输入，一次覆盖所有页面
- **Suggested next action:** 执行 PAGINATION-UX-FIX worker

---

## Backlog / Observations


