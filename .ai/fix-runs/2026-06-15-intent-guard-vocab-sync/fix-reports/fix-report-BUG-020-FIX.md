# Fix Report: BUG-020-FIX

## Ticket Info
- **Review Task:** open-bugs.md
- **Affected Task:** F23-T01 — BUG-020 — F23 bare vocabulary queries blocked by F19 intent guard
- **Criterion:** BUG-020
- **Files Declared:** backend/app/services/ai_search/service.py

## Files Changed
- `backend/app/services/ai_search/service.py`

## Patch Summary
Added one new `re.compile(...)` entry to `_PROPERTY_SEARCH_PATTERNS` in `backend/app/services/ai_search/service.py`. The new pattern matches the 9 F23 bare vocabulary terms exactly so those queries are recognized as property searches without changing `_is_property_search` or any existing pattern.

## Open Issues
None

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec -T backend python3 -c "import app.main; print('OK')"` | `OK` | **PASS** |
