# F17 Parser Semantic Expansion — Tasks

---

## T01 — Codex: Backend

- **owner:** codex
- **type:** build
- **depends_on:** none
- **allowed files:** see owner.md T01

### LLM prompt extension

Extend the prompt in `_parse_filters` (`backend/app/services/ai_search/service.py`) to request:

```
bedrooms_subjective_label : "insufficient" | "excessive" | "adequate" | "unknown" | null
bedrooms_ref              : integer | null
bathrooms_subjective_label: "insufficient" | "excessive" | "adequate" | "unknown" | null
bathrooms_ref             : integer | null
```

Only extract a label when the user expresses a judgment about an explicit count N. If no count is stated, `*_ref` must be null and label must be `unknown` or null.

### Deterministic mapping step

After the LLM call, add a mapping step in `_parse_filters` before calling `_normalize_filters`:

- `bedrooms_subjective_label == "insufficient"` and `bedrooms_ref is not None` and `bedrooms_min` not already set by F16 → `bedrooms_min = bedrooms_ref + 1`
- `bedrooms_subjective_label == "excessive"` and `bedrooms_ref is not None` and `bedrooms_max` not already set by F16 → `bedrooms_max = bedrooms_ref - 1`
- `adequate`, `unknown`, or null ref → no filter set
- Same logic for `bathrooms_*`

F16 deterministic values always take priority (do not overwrite already-set fields).

### Integration test file

Create `backend/tests/test_subjective_eval.py`:
- Mark tests `@pytest.mark.integration`
- Call `_parse_filters` directly (not the full `ai_search` endpoint)
- Assert the resulting `SearchFilters` fields match expected values
- Minimum 8 cases covering Chinese/English, bedrooms/bathrooms, combined with F16 filters

Example cases:
```python
("两个浴室太少",                SearchFilters(bathrooms_min=3)),
("三个卧室不够用",              SearchFilters(bedrooms_min=4)),
("4个卧室太多",                SearchFilters(bedrooms_max=3)),
("2 bedrooms not enough",      SearchFilters(bedrooms_min=3)),
("5 bathrooms too many",       SearchFilters(bathrooms_max=4)),
("两个卧室太少 预算2000万",    SearchFilters(bedrooms_min=3, max_price=20000000)),
("3间卧室不够 预算1500w",      SearchFilters(bedrooms_min=4, max_price=15000000)),
("一个浴室不够用 两间卧室太少", SearchFilters(bathrooms_min=2, bedrooms_min=3)),
```

### Verification

```bash
docker compose exec backend python -c "import app.main; print('OK')"
docker compose exec backend python -m pytest tests/test_eval.py -v
```

---

## T02 — Codex: Review

- **owner:** codex
- **type:** review
- **depends_on:** T01

Review against `acceptance.md`. Read-only, no source file modifications.

---

## T03 — Claude: Acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T02
