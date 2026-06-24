## Disposition: ACCEPTED

# F27 Need Interpretation Layer — Final Acceptance Report

T04 Codex review verdict: **PASS** (all A1–A39 criteria passed, no issues found, no required fixes).

## Criteria Verification

| ID | Criterion | Result | Evidence |
|----|-----------|--------|----------|
| A1 | `_is_property_search("一室两厅")` → True | PASS | Codex verified in backend container |
| A2 | `_is_property_search("一室两厅 一家三口")` → True | PASS | Codex verified in backend container |
| A3 | `_is_property_search("两房一厅")` → True | PASS | Codex verified in backend container |
| A4 | `_is_property_search("三室两卫")` → True | PASS | Codex verified in backend container |
| A5 | Chinese digit normalization before pattern match | PASS | Code inspection: `_CHINESE_DIGIT_RE` applied at entry |
| A6 | Non-search query "为什么房价上涨" → rejected | PASS | Codex verified in backend container |
| A7 | `_extract_living_rooms("一室两厅")` → 2 | PASS | Codex verified; test_eval_f27.py covers case |
| A8 | `_extract_living_rooms("三室两厅")` → 2 | PASS | test_eval_f27.py covers case |
| A9 | `_extract_living_rooms("两室一厅")` → 1 | PASS | test_eval_f27.py covers case |
| A10 | `_extract_living_rooms("两室")` → None | PASS | test_eval_f27.py covers case |
| A11 | interpreted_intent includes living_rooms IntentField | PASS | test_eval_f27.py asserts the payload |
| A12 | living_rooms filterable=False, not in SearchFilters | PASS | Code inspection + test assertion |
| A13 | "一家三口" → household_size=3 | PASS | eval_set_f27.json + test_eval_f27.py |
| A14 | "一家四口" + bedrooms_min=3 → no tension | PASS | eval_set_f27.json case covered |
| A15 | "适合老人住" → lifestyle need | PASS | eval_set_f27.json case covered |
| A16 | "安静一点" → quiet_environment=True | PASS | eval_set_f27.json case covered |
| A17 | "靠近好学校" → unresolved, not needs | PASS | eval_set_f27.json case covered |
| A18 | Unknown NeedType → silently discarded | PASS | `test_interpret_needs_discards_unknown_type` — 28/28 pass |
| A19 | `_interpret_needs` exception → empty default, search unaffected | PASS | `test_ai_search_interpret_needs_exception_returns_empty_default` — 28/28 pass |
| A20 | bedrooms_min=1, household_size=3 → tension notice | PASS | test_detect_tensions_cases asserts notice text |
| A21 | bedrooms_min=3, household_size=4 → no tension | PASS | test_detect_tensions_cases covers case |
| A22 | `_detect_tensions` is pure Python, no LLM | PASS | Code inspection: no `complete()` call in function |
| A23 | bedrooms_min=None → no tension notice | PASS | `_detect_tensions` returns [] immediately if None |
| A24 | AiSearchResult has interpreted_intent + interpreted_needs with defaults | PASS | schemas/ai_search.py; frontend/types/ai-search.ts |
| A25 | Existing AiSearchResult fields unchanged | PASS | Code inspection; A37 non-regression passes |
| A26 | `import app.main` exits 0 | PASS | Codex verified in backend container |
| A27 | `npx tsc --noEmit` exits 0 | PASS | Codex verified during review |
| A28 | Tension notice renders amber-50/amber-600 + ⚠️ | PASS | interpreted-needs-card.tsx line 32 (after direct_fixup) |
| A29 | filterable=false → dashed chip + "（暂无数据）" | PASS | interpreted-needs-card.tsx lines 72–82 |
| A30 | needs raw renders as gray small tags | PASS | interpreted-needs-card.tsx lines 57–64 |
| A31 | unresolved renders as small gray helper text | PASS | interpreted-needs-card.tsx lines 88–91 |
| A32 | All empty → returns null | PASS | isEmpty guard at lines 18–22 |
| A33 | No shadcn components; Tailwind only | PASS | Code inspection: only Tailwind classes used |
| A34 | eval_set_f27.json ≥ 8 cases | PASS | 8 cases covering all spec types |
| A35 | BUG-026 regression test present | PASS | test_f27_property_search_and_filter_parsing[bug_026_entry] |
| A36 | tension detection assertion present | PASS | test_detect_tensions_cases[one_room_two_living_three_person_family] |
| A37 | F16 eval 30/30 unchanged | PASS | `bash tools/run_eval.sh` → 2 passed (both threshold tests) |
| A38 | `_parse_filters` source unchanged | PASS | Codex git diff confirmed |
| A39 | `_relax_filters`/`_apply_relaxation` unchanged | PASS | Codex git diff confirmed |

## Notes
- tools/*.sh changes (Antigravity CLI migration + Codex binary local-priority fix) are pre-authorized orchestrator infrastructure changes. Codex review accepted them as such.
- A18 and A19 test coverage was added via direct_fixup after T04 second FAIL. All 28 F27 tests pass.
- BUG-026 is fixed and merged into this feature as specified.
