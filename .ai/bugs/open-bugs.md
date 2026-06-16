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

### BUG-021 — AI search "Understood Filters" missing F22 fields

- **Status:** open
- **Severity:** P2 / High — F22/F23 filters applied correctly but invisible to user
- **Source:** F23 smoke test 2026-06-16
- **Description:** `ai-parsed-filters-card.tsx` renders chips only for `location`, `min_price`, `max_price`, `bedrooms_min/max`, `bathrooms_min/max`, `status`. The four F22 fields (`area_min`, `area_max`, `built_year_min`, `subway_distance_max`) are absent. Backend returns them correctly; frontend silently ignores them, showing "No specific filters parsed" even when filters are active.
- **Fix:** Add chip rendering for the four missing fields in `renderChips()`. No other files.
- **Fix run:** [2026-06-16-ai-filters-card-f22-fields](../fix-runs/2026-06-16-ai-filters-card-f22-fields/fix-tickets.md)



## Skipped Tests


## Backlog / Observations


