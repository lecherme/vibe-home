# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | `backend/migrations/003_create_property_embeddings.sql` contains `vector` extension, `property_embeddings`, and `match_property_embeddings`. |
| A2 | PASS | `backend/requirements.txt` includes `openai` and `anthropic`. |
| A3 | PASS | `backend/app/core/config.py` has `OPENAI_API_KEY`, `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL`; no `ANTHROPIC_*` fields remain. |
| A4 | PASS | `embed_text`, `try_upsert_property_embedding`, and `semantic_search` exist in `backend/app/services/embeddings/service.py`. |
| A4b | PASS | `complete(prompt, max_tokens, temperature)` exists and branches for `anthropic`, `openai`, `openai_compatible` in `backend/app/services/llm/service.py`. |
| A5 | PASS | `try_upsert_property_embedding` wraps embed/upsert in `try/except` and logs `warning` only. |
| A6 | PASS | `backend/app/services/ai_search/service.py` returns HTTP 503 when `OPENAI_API_KEY` or `LLM_API_KEY` is missing. |
| A7 | PASS | Query parsing failure is caught and returns `query_parsed=False` without surfacing the exception. |
| A8 | FAIL | On semantic failure with empty parsed filters, `_resolve_result_ids()` falls back to keyword search, not pure filter search (`backend/app/services/ai_search/service.py:159-178`). Reproduced via inline docker exec patching. |
| A9 | PASS | `POST /api/v1/search/ai` exists, depends on `get_current_user`, and is registered in `app.main`. |
| A10 | PASS | `POST /api/v1/admin/embeddings/sync` exists, is admin-gated via `require_role("admin")`, and is registered. |
| A11 | PASS | `create_property` and `update_property` call `try_upsert_property_embedding` before returning. |
| A12 | PASS | `docker compose exec backend python -c "import app.main; print('OK')"` returned `OK` on 2026-06-08. |
| A13 | PASS | `AiSearchRequest` and `AiSearchResult` are published in `frontend/types/search.ts`. |
| A14 | PASS | `frontend/lib/api/ai-search.ts` exports `aiSearch()` and `AiSearchApiError` carries `status`. |
| A15 | PASS | `AiSearchBar` has input + button, Enter triggers search, loading disables input/button, and button classes are explicit Tailwind colors. |
| A16 | PASS | `AiParsedFiltersCard` shows fallback copy when `queryParsed=false`, otherwise renders chips and summary. |
| A17 | PASS | `/search` includes `"Filter Search"` and `"✨ AI Search"` tabs and preserves both modes. |
| A18 | PASS | AI mode renders an error banner on failure in `frontend/app/(dashboard)/search/page.tsx`. |
| A19 | PASS | AI mode shows a no-results empty state when there are no items. |
| A20 | PASS | Existing filter-search flow remains in place; standard search UI/API path is still present and `/api/v1/properties/search` was not touched. |
| A21 | PASS | `npx tsc --noEmit` exited 0 in `frontend/` on 2026-06-08. |
| A22 | PASS | Static review supports tab switching and retained filter mode; manual exercise remains for T04. |
| A23 | PASS | Static review shows end-to-end NL query wiring for results, parsed filters card, and summary; manual exercise remains for T04. |
| A24 | PASS | Static review shows missing-key 503 path in backend and AI error banner handling in frontend; manual exercise remains for T04. |

## Issues Found
- BLOCKER: `backend/app/services/ai_search/service.py:159-178` violates A8. If semantic search fails and parsed filters are empty, the code returns keyword fallback instead of pure filter-search results.
- WARNING: `backend/app/services/ai_search/service.py:205-209` continues to call the LLM for summary generation even after query parsing failure set `query_parsed=False`. That does not fully match the spec fallback contract of degrading cleanly after AI failure.
- WARNING: `backend/app/api/v1/admin/router.py:48-57` returns `{"synced": len(properties)}` even though failed embedding upserts are skipped and only logged, so the reported count is attempted, not successful.
- WARNING: No automated tests were added for the new AI search and embeddings paths; the missed A8 edge case is exactly the kind of regression this left uncovered.
- MINOR: `status.json` is modified in the working tree, but the diff is Claude runtime bookkeeping for T03 start; I found no evidence of Codex or Gemini modifying it.

## Required Fixes
- Change AI search fallback so a semantic-step failure returns pure filter-search results, including the empty-filter case, instead of keyword fallback.

## Approved Items
- Backend migration, config, embedding service, LLM abstraction, AI search router, and admin sync endpoint are all present and wired.
- Frontend request/response API types are published under `frontend/types/search.ts`.
- The new frontend leaf components are presentational; the API-calling/search orchestration remains outside them.
- `/api/v1/properties/search` behavior was not modified.
