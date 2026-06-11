# F18 — Parser Room Vocabulary Expansion

## Problem

The deterministic parser in `_normalize_query` misses high-frequency Chinese real-estate room vocabulary and bare count expressions, causing two failure modes:

1. **Vocabulary gap**: Queries using `卫生间`, `洗手间`, `室`, `卧`, `卫` fall through to the LLM, which may misinterpret explicit comparator expressions as subjective labels (e.g. "3个卫生间以上" → `bathrooms_max=2` instead of `bathrooms_min=3`).

2. **Bare count gap**: Queries with no comparator and no subjective judgment (e.g. "2个卧室 预算2000w") produce no room filter at all.

## Scope

Pure deterministic changes to `backend/app/services/ai_search/service.py`. No LLM prompt changes, no schema changes, no frontend changes.

### In scope

**1. Vocabulary additions**

Extend `_BATHROOM_PATTERN` and `_BEDROOM_PATTERN` with common Chinese synonyms and shorthands:

- Bathroom: add `卫生间`, `洗手间` to `_BATHROOM_PATTERN`
- Bedroom: no change needed for 卧室/房间
- Single-char shorthands `室`, `卧`, `卫` must only be matched inside digit-bounded room-count patterns, not added as free-standing global alternations in `_BEDROOM_PATTERN` / `_BATHROOM_PATTERN`. This avoids false matches against words like 室内, 卫星.

**2. Bare room count**

New pattern: `N个卧室` / `N间卧室` / `N室` / `N卧` (no comparator) → `bedrooms_min=N`

New pattern: `N个浴室` / `N个卫生间` / `N卫` (no comparator) → `bathrooms_min=N`

Applied after the existing comparator-based extraction so already-consumed tokens are not double-matched.

**3. English bare count**

`N bedrooms` / `N beds` (no comparator) → `bedrooms_min=N`
`N bathrooms` / `N baths` (no comparator) → `bathrooms_min=N`

### Product decision

Bare count (`N个卧室`) maps to `bedrooms_min=N`, not exact match. Rationale: users expressing a count without a comparator almost always mean "at least N", not "exactly N".

F18 does not introduce exact-match room filtering. Bare N maps to `_min=N` only. Subjective adequacy expressions such as "刚好N间" remain non-filtering by current product design (F17 adequate path).

### Out of scope

- Compound expressions: `3室2卫`, `两房一厅两卫` (F19)
- LLM middle layer / `room_mentions` schema (F19)
- Price vocabulary changes
- Any frontend change

## Files

- `backend/app/services/ai_search/service.py` — only file to modify

## Eval protection

`backend/tests/test_eval.py` and `backend/tests/eval_set.json` must remain unchanged and pass 30/30.
