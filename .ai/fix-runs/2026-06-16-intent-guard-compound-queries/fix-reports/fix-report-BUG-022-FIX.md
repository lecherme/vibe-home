# Fix Report: BUG-022-FIX

## Ticket Info
- **Review Task:** open-bugs.md
- **Affected Task:** F19 — BUG-022 — Intent guard non-deterministic for compound queries
- **Criterion:** BUG-022
- **Files Declared:** backend/app/services/ai_search/service.py

## Files Changed
- backend/app/services/ai_search/service.py

## Patch Summary
Removed the `^` and `$` anchors from the `_PROPERTY_SEARCH_PATTERNS` entry that matches terms like `近地铁` and `新楼` in `backend/app/services/ai_search/service.py`. This changes the pattern from full-string matching to substring matching so compound queries such as `近地铁 四房` are recognized.

## Open Issues
None

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec -T backend python3 -c "import app.main; print('OK')"` | `OK` | **PASS** |
