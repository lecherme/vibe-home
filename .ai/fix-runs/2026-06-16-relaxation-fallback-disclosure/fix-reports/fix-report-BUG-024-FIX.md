# Fix Report: BUG-024-FIX

## Ticket Info
- **Review Task:** open-bugs.md
- **Affected Task:** F20 — BUG-024 — Relaxation fallback summary 丢失放宽说明
- **Criterion:** BUG-024
- **Files Declared:** backend/app/services/ai_search/service.py

## Files Changed
- backend/app/services/ai_search/service.py

## Patch Summary
Replaced the `ai_search()` summary fallback string in `backend/app/services/ai_search/service.py` so that when `relaxed_conditions` is non-empty, the fallback summary explicitly says the search conditions were relaxed. The existing fallback message is unchanged when no relaxation occurred.

## Open Issues
None

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec -T backend python3 -c "import app.main; print('OK')"` | `OK` | **PASS** |
