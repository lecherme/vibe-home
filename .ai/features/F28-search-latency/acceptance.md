# F28 — Acceptance Criteria

T06 (Codex review) verifies every criterion below and writes `review.md`.
T07 (Claude acceptance) reads `review.md` and writes `final-report.md`.

---

## Instrumentation

| ID | Criterion |
|----|-----------|
| A1 | After any property search, a structured INFO log entry is emitted with field `parse_filters_ms` (integer) |
| A2 | Same log entry contains `interpret_needs_ms`, `resolve_ids_ms`, `collect_items_ms`, `total_ms` (all integers) |
| A3 | Same log entry contains `query` field for correlation |
| A4 | Log entry is emitted at the END of `ai_search()`, not mid-function |

## Parallelization

| ID | Criterion |
|----|-----------|
| A5 | `_interpret_needs` and `_resolve_result_ids` are both submitted to a `ThreadPoolExecutor` before either `.result()` is awaited |
| A6 | Test asserts that both futures are created before either result is retrieved |
| A7 | When `_interpret_needs` raises an exception, `_resolve_result_ids` result is still used and the search returns normally with empty `interpreted_needs` |
| A8 | Test covers the `_interpret_needs` failure-isolation path |

## Summary decoupling

| ID | Criterion |
|----|-----------|
| A9 | `ai_search()` does NOT call `_generate_summary` |
| A10 | `ai_search()` generates a UUID, stores `SummaryContext` in an in-process TTLCache, and returns `search_request_id=<uuid>` |
| A11 | `AiSearchResult.ai_summary` returns `""` (empty string) on every main search call |
| A12 | `AiSearchResult.search_request_id` is a new `Optional[str]` field; old clients that ignore it are unaffected |
| A13 | `POST /api/v1/search/ai/summary` endpoint exists |
| A14 | Summary endpoint accepts `{search_request_id}`, looks up server-stored context (no client-supplied items/filters), calls `_generate_summary`, returns `{ai_summary: str}` |
| A15 | Summary endpoint returns 404 for unknown or expired `search_request_id` |
| A16 | Context entry is removed from store after being served (one-shot) |
| A17 | TTLCache is bounded (max 512 entries, TTL 120 s) |
| A18 | `frontend/types/ai-search.ts` updated: `ai_summary: string`, `search_request_id?: string` |
| A19 | `frontend/lib/api/search.ts` exports a `fetchSearchSummary(search_request_id)` function |
| A20 | `npx tsc --noEmit` exits 0 |

## Frontend deferred summary

| ID | Criterion |
|----|-----------|
| A21 | When main results render with `ai_summary === ""` and `search_request_id` set, a "Generating summary…" placeholder is displayed |
| A22 | Secondary request to summary endpoint fires after results render |
| A23 | Summary text replaces placeholder on arrival |
| A24 | If secondary request fails, placeholder is silently removed (no error shown) |
| A25 | `npx tsc --noEmit` exits 0 after T04 changes |

## Non-regression

| ID | Criterion |
|----|-----------|
| A26 | `bash tools/run_eval.sh` exits 0 (F16 eval unchanged) |
| A27 | F27 eval passes: `docker compose run --rm -v $(pwd)/backend/tests:/app/tests backend python3 -m pytest /app/tests/test_eval_f27.py -q` exits 0 |

---

## Review and Acceptance

If review verdict is FAIL, Claude does NOT proceed directly to T07 acceptance.
Claude must:
1. Write `last_review_failure` to `status.json` with fix_path, failed_criteria, and fix_instructions.
2. Choose fix_path: task_retry, direct_fixup, or review_rerun.
3. Apply the fix and re-run review before acceptance.

## Rejection Conditions

- Any worker modifies `status.json`
- Summary endpoint accepts client-supplied items or filters (must use server-stored context only)
- `ai_summary` field type changed to `Optional[str]` (must stay `str`, empty string default)
- Gemini modifies `frontend/lib/api/` or `frontend/types/`
- F16 or F27 eval regresses
