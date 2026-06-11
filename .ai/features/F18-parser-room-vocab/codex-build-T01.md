# Codex Build Report

## Task Completed
- T01

## Files Changed
- `backend/app/services/ai_search/service.py`

## API Types Published
- None

## Tests Written
- None

## Summary

Three additions to `_normalize_query` in `backend/app/services/ai_search/service.py`:

**1. Vocabulary expansion**
Added `卫生间` and `洗手间` to `_BATHROOM_PATTERN`. These are the most common Chinese terms for bathroom in real-estate queries and were previously falling through to the LLM, causing misclassification.

**2. Digit-bounded single-char shorthand passes**
New `_extract_shorthand_comparator` function handles `N室`/`N卧` (bedrooms) and `N卫` (bathrooms) with comparators. These are matched only in digit-bounded patterns to avoid false matches on words like 室内, 卫星. Applied after the standard `_extract_room_bounds` passes.

**3. Bare room count extraction**
New `_extract_bare_count` function applied after all comparator passes. Maps `N + room noun (no comparator)` to `_min = N`:
- `N个卧室` / `N间卧室` / `N室` / `N卧` / `N bedrooms` / `N beds` → `bedrooms_min=N`
- `N个浴室` / `N个卫生间` / `N个洗手间` / `N卫` / `N bathrooms` / `N baths` → `bathrooms_min=N`

Negative lookaheads on single-char bare patterns prevent double-matching already-consumed comparator expressions and guard against `卫生间` / `卫星` collisions.

## Verification

`docker compose exec backend python -c "import app.main; print('OK')"` → OK

## Open Issues

- None
