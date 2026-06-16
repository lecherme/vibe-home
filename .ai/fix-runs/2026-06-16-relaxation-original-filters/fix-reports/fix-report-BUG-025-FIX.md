# Fix Report: BUG-025-FIX

## Ticket Info
- **Review Task:** open-bugs.md
- **Affected Task:** F20 — BUG-025 — parsed_filters should preserve original filters when relaxation occurs
- **Criterion:** BUG-025
- **Files Declared:** backend/app/services/ai_search/service.py

## Files Changed
- backend/app/services/ai_search/service.py

## Patch Summary
Saved a copy of the originally parsed `SearchFilters` in `ai_search()` before any relaxation logic runs. Replaced the final `AiSearchResult.parsed_filters` assignment so the API response returns the user’s original filters instead of the relaxed search state.

## Open Issues
None.

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec -T backend python3 -c "import app.main; print('OK')"` | `OK` | **PASS** |
