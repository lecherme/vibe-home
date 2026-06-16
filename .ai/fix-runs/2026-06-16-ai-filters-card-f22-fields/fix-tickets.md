# Fix Tickets — 2026-06-16 AI filters card F22 fields

Standalone fix for BUG-021: AI search "Understood Filters" missing F22 fields.
Source: `.ai/bugs/open-bugs.md`

---

## BUG-021-FIX

- **Bug:** BUG-021 — AI search "Understood Filters" missing F22 fields
- **Owner:** Codex
- **Severity:** P2 / High
- **Allowed files:**
  1. `frontend/components/features/search/ai-parsed-filters-card.tsx`
- **Requirements:**
  1. In `renderChips()`, add visible chip display for the four F22 fields that are currently missing: `area_min`, `area_max`, `built_year_min`, `subway_distance_max`
  2. Each chip must accurately represent the filter value (e.g. area range, minimum built year, maximum subway distance)
  3. Chip style must be consistent with the existing chips in the same component
  4. Only modify this one component file; no other files
  5. TypeScript check must pass: `docker compose exec frontend npx tsc --noEmit` exit 0
- **Verification:** `docker compose exec frontend npx tsc --noEmit` exit 0
- **Status:** pending
