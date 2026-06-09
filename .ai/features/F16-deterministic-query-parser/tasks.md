# F16 Deterministic Query Parser — Tasks

---

## T01 — Codex: Backend

- **owner:** codex
- **type:** build
- **depends_on:** none
- **allowed files:** see owner.md T01

### SearchFilters schema

Update `backend/app/schemas/search.py`:
- Remove `bedrooms: int | None` and `bathrooms: int | None`
- Add `bedrooms_min`, `bedrooms_max`, `bathrooms_min`, `bathrooms_max` (all `int | None`)

### Search service

Update `backend/app/services/search/service.py`:
- Replace `filters.bedrooms` with `bedrooms_min/max` checks (`< bedrooms_min` skip, `> bedrooms_max` skip)
- Replace `filters.bathrooms` with `bathrooms_min/max` checks

### Filter search API

Update `backend/app/api/v1/search/router.py` (or equivalent):
- Rename query param `bedrooms` → `bedrooms_min`; add `bedrooms_max`, `bathrooms_min`, `bathrooms_max`

### Normalization layer

New function `_normalize_query(query: str) -> dict` in `backend/app/services/ai_search/service.py`:

Rules (applied in order, case-insensitive):
1. Price unit: `(\d+(?:\.\d+)?)\s*(w|万)` → multiply by 10000 → integer
2. Budget/upper-bound price keywords (`预算`, `budget`, `不超过`, `以内`, `under`, `below`) + extracted price → `max_price`
3. Lower-bound price keywords (`至少`, `最少`, `at least`) + extracted price → `min_price`
4. Bedroom/bathroom extraction with comparator:
   - `(\d+)\s*(个)?\s*(卧室|房间|bedrooms?|beds?)` + `以上|at least|or more|or above` → `bedrooms_min = X`
   - `(\d+)\s*(个)?\s*(卧室|房间|bedrooms?|beds?)` + `more than|greater than|超过` → `bedrooms_min = X + 1`
   - `(\d+)\s*(个)?\s*(卧室|房间|bedrooms?|beds?)` + `以下|at most|不超过|or below` → `bedrooms_max = X`
   - `(\d+)\s*(个)?\s*(卧室|房间|bedrooms?|beds?)` + `less than|fewer than|少于` → `bedrooms_max = X - 1`
   - Same patterns for `浴室|bathrooms?|baths?` → `bathrooms_min/max`
5. Return dict with extracted numeric fields; unmatched text passed to LLM

### AI search service update

Update `_parse_filters` in `backend/app/services/ai_search/service.py`:
1. Call `_normalize_query(query)` first → get deterministic fields
2. LLM call with simplified prompt: only request `location`, `status`, unresolved fuzzy remainder; do not ask for price/bedroom/bathroom (already extracted)
3. Merge: deterministic fields override LLM output for same keys
4. Map to `SearchFilters` using new field names

Update `_normalize_filters` accordingly.

### Eval set

Create `backend/tests/eval_set.json` with >= 25 queries covering:
- Chinese price with 万/w
- English price with hkd
- Chinese comparison words (以上/以下/超过/少于)
- English comparison words (more than/at least/under/fewer than)
- Mixed Chinese/English
- Location-only queries
- Combined filters

Create `backend/tests/test_eval.py` that runs each query through `_normalize_query` and checks all non-null expected fields match.

### Verification

```bash
docker compose exec backend python -c "import app.main; print('OK')"
docker compose exec backend python -m pytest tests/test_eval.py -v
```

---

## T02 — Gemini: Frontend

- **owner:** gemini
- **type:** build
- **depends_on:** T01
- **allowed files:** see owner.md T02

### Types

Update `frontend/types/search.ts`:
- Remove `bedrooms?: number` and `bathrooms?: number` from `SearchFilters`
- Add `bedrooms_min?: number`, `bedrooms_max?: number`, `bathrooms_min?: number`, `bathrooms_max?: number`

### AiParsedFiltersCard chips

Update `frontend/components/features/search/ai-parsed-filters-card.tsx`:
- `bedrooms_min` only → `>= X Beds`
- `bedrooms_max` only → `<= X Beds`
- Both → `X–Y Beds`
- Same logic for bathrooms

### Filter search form / API client

Update any filter search query param construction to use `bedrooms_min` instead of `bedrooms`, and add `bedrooms_max`, `bathrooms_min`, `bathrooms_max` if previously missing.

### Verification

```bash
docker compose exec frontend npx tsc --noEmit
```

---

## T03 — Codex: Review

- **owner:** codex
- **type:** review
- **depends_on:** T01, T02

Review against acceptance.md. Read-only, no source file modifications.

---

## T04 — Claude: Acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T03
