# F18 Tasks

## T01 — Implementation (Codex)

Modify `backend/app/services/ai_search/service.py`:

1. Add `卫生间`, `洗手间` to `_BATHROOM_PATTERN`.
2. Extend `_extract_room_bounds` to support `室`/`卧` (bedroom) and `卫` (bathroom) as field nouns inside the existing digit-bounded patterns only — not as global alternations.
3. Add a bare-count extraction pass after the comparator pass: `N + room noun (no comparator)` → `_min = N` for both bedrooms and bathrooms.
4. Ensure English bare counts (`N bedrooms`, `N bathrooms`) are covered by the same bare-count pass.

Verify: `import app.main` exit 0 in container.

## T02 — Review (Codex)

Read-only review against acceptance criteria A1–A16. No source file changes.

## T03 — Acceptance (Claude)

Manual verification of A1–A5 by code inspection and A6–A16 via `_parse_filters` in container. Write `final-report.md`.
