# F27 Need Interpretation Layer — Tasks

Every task has exactly one owner. Collaboration happens through sequential tasks, not shared tasks.

---

## T01 — Codex: backend + BUG-026 + frontend types

- **owner:** codex
- **type:** build
- **depends_on:** none
- **title:** Backend schema additions, BUG-026 fix, need interpretation service, and frontend type sync

**Scope:**
- `backend/app/schemas/ai_search.py` — add IntentField, UserNeed, SearchNotice, InterpretedNeeds; extend AiSearchResult with interpreted_intent + interpreted_needs
- `backend/app/services/ai_search/service.py` — fix `_is_property_search` (BUG-026); add `_LIVING_ROOM_PATTERN`, `_extract_living_rooms`, `_interpret_needs`, `_detect_tensions`; update `ai_search()` main flow
- `frontend/types/ai-search.ts` — add IntentField, NeedType, NoticeType, UserNeed, SearchNotice, InterpretedNeeds; extend AiSearchResult with `interpreted_intent?` and `interpreted_needs?`
- `.ai/features/F27-need-interpretation/tension-policy.md` — new, document V1 tension rules

**Done condition:** `import app.main` exits 0; `_is_property_search("一室两厅")` returns True; `_extract_living_rooms("一室两厅")` returns 2; tension notice generated for household_size=3 + bedrooms_min=1; `npx tsc --noEmit` exits 0.

---

## T02 — Gemini: frontend UI rendering

- **owner:** gemini
- **type:** build
- **depends_on:** T01
- **title:** InterpretedNeedsCard component and search page integration

**Scope:**
- `frontend/components/features/search/interpreted-needs-card.tsx` — new component (Tailwind only, no shadcn)
- `frontend/app/(dashboard)/search/page.tsx` — integrate InterpretedNeedsCard below ai-parsed-filters-card

**Done condition:** `npx tsc --noEmit` exits 0; tension notice renders as amber chip with ⚠️; filterable=false intent renders with dashed border + "（暂无数据）"; all-empty state renders nothing.

---

## T03 — Codex: evaluation set

- **owner:** codex
- **type:** build
- **depends_on:** T01
- **title:** F27 evaluation set and test suite

**Scope:**
- `backend/tests/eval_set_f27.json` — new, ≥8 cases covering all spec case types
- `backend/tests/test_eval_f27.py` — new, assertions for BUG-026 regression + interpreted_intent + needs + notices + unresolved

**Done condition:** Test file covers: 一室两厅 enters pipeline (BUG-026), living_rooms extraction, tension detection (household_size > bedrooms+1), no-tension case, unresolved passthrough, non-search query.

---

## T04 — Codex: review

- **owner:** codex
- **type:** review
- **depends_on:** T01, T02, T03
- **title:** Review F27 implementation against acceptance criteria

**Scope:**
- Validate all deliverables against `acceptance.md`.
- Check ownership boundaries and artifacts.
- Write `review.md`.

**Done condition:** `review.md` written with PASS/FAIL verdict and per-criterion results.

---

## T05 — Claude: acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T04
- **title:** Validate F27 and write final acceptance result

**Scope:**
- Read `review.md`.
- Write `final-report.md` with disposition `accepted` or `failed`.
- Update `status.json` feature status to `done` or `failed`.

**Done condition:** `final-report.md` written and `status.json` updated.
