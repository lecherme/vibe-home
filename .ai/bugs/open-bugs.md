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

### BUG-024 — Relaxation fallback summary 丢失放宽说明

- **Status:** open
- **Severity:** P2 / High — LLM summary 失败时用户误以为 relaxed 结果也满足原始条件
- **Source:** F23 smoke test 2026-06-16
- **Description:** `ai_search()` 在 `_generate_summary` 抛出异常时回退到 `f"Found {total} properties matching your search."`，无论是否发生了 relaxation。当 `relaxed_conditions` 非空时，用户看不到"结果已放宽"的提示，误以为所有结果都满足原始过滤条件（如 >= 4 Beds）。
- **Fix:** 在 `ai_search()` 的 summary fallback 分支（line 861）中，当 `relaxed_conditions` 非空时，生成含放宽说明的 fallback 文案。不改 parser、search、前端。
- **Fix run:** [2026-06-16-relaxation-fallback-disclosure](../fix-runs/2026-06-16-relaxation-fallback-disclosure/fix-tickets.md)





## Skipped Tests


## Backlog / Observations


