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


### BUG-017 — Admin 分页无直接跳页输入
- **Severity:** P3 · Low
- **Status:** backlog
- **Source:** BUG-011-FIX 复测 2026-05-25
- **Summary:** Admin 房源列表分页只有 Previous/Next，无法直接输入或点击具体页码跳转（如 "跳到第 5 页"）；数据量大时体验差
- **Suggested next action:** 在分页区加页码输入框或页码按钮列表；产品确认 UI 风格后开 fix ticket

---

## Backlog / Observations


