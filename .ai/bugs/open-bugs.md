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

### BUG-023 — 中文数字房间词不解析为 bedrooms_min

- **Status:** open
- **Severity:** P2 / High — 用户输入 "四房"/"三房" 等核心条件被丢弃
- **Source:** F23 smoke test 2026-06-16
- **Description:** `_normalize_query` 已将中文数字转换为阿拉伯数字（"四" → "4"），但 bedroom 确定性 pattern 只覆盖 `\d+室`、`\d+卧`、`\d+bedrooms`，没有 `\d+房`。"四房" 转换后变成 "4房"，没有任何 pattern 命中，`bedrooms_min` 始终为 null。
- **Fix:** 在 `_normalize_query` 的 `_extract_bare_count` 调用组里补一条 `\d+房` pattern，带负向前瞻排除 "房源"/"房子"/"房价"/"房间"/"房龄"/"房东" 等歧义词。仅修改该函数内的 pattern 列表，不改其他函数。
- **Fix run:** [2026-06-16-chinese-room-vocab](../fix-runs/2026-06-16-chinese-room-vocab/fix-tickets.md)




## Skipped Tests


## Backlog / Observations


