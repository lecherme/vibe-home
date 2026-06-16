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

### BUG-020 — F23 bare vocabulary queries blocked by F19 intent guard

- **Status:** open
- **Severity:** P2 / High — core F23 feature non-functional for bare vocabulary queries
- **Source:** F23 smoke test 2026-06-15
- **Description:** Bare preference queries supported by F23 (`新楼`, `次新房`, `近地铁` etc.) are incorrectly classified as non-property-search by `_is_property_search`. `_PROPERTY_SEARCH_PATTERNS` was never updated when F23 vocabulary was added, so these queries fall through to the LLM classifier which returns `false` for bare single-term queries. Result: user sees "not a property search" redirect instead of filtered results.
- **Fix:** Add one pattern to `_PROPERTY_SEARCH_PATTERNS` covering all 9 F23 vocabulary terms. Do not modify `_is_property_search` function body.
- **Fix run:** [2026-06-15-intent-guard-vocab-sync](../fix-runs/2026-06-15-intent-guard-vocab-sync/fix-tickets.md)


## Skipped Tests


## Backlog / Observations


