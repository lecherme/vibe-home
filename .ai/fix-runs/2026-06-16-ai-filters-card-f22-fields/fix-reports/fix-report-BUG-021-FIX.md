# Fix Report: BUG-021-FIX

## Ticket Info
- **Review Task:** open-bugs.md
- **Affected Task:** F22 — BUG-021 — AI search Understood Filters missing F22 fields
- **Criterion:** BUG-021
- **Files Declared:** frontend/components/features/search/ai-parsed-filters-card.tsx

## Files Changed
- `frontend/components/features/search/ai-parsed-filters-card.tsx`

## Patch Summary
Added missing `renderChips()` cases for `area_min`/`area_max`, `built_year_min`, and `subway_distance_max` in `frontend/components/features/search/ai-parsed-filters-card.tsx`. The new chips follow the existing badge pattern and use app-consistent units for area (`m²`) and subway distance (`m`).

## Open Issues
None

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec frontend npx tsc --noEmit` | exit 0, no output | **PASS** |

## Direct fixup applied
Codex wrote `<=` inside JSX text which is invalid (parsed as tag opener). Replaced with `≤` Unicode character. tsc then passes.
