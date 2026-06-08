# Review

## Verdict
PASS

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | [003_create_property_embeddings.sql](/home/lecherme/workspace/vibe-home/backend/migrations/003_create_property_embeddings.sql:1) creates `vector`, `property_embeddings`, and `match_property_embeddings`. |
| A2 | PASS | `openai` and `anthropic` are present in [requirements.txt](/home/lecherme/workspace/vibe-home/backend/requirements.txt:11). |
| A3 | PASS | New embedding/LLM settings exist and legacy `OPENAI_API_KEY` / `ANTHROPIC_*` fields are absent in [config.py](/home/lecherme/workspace/vibe-home/backend/app/core/config.py:18). |
| A4 | PASS | `embed_text`, `try_upsert_property_embedding`, and `semantic_search` exist in [embeddings/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/embeddings/service.py:35). |
| A4b | PASS | `complete(prompt, max_tokens, temperature)` supports `anthropic`, `openai`, and `openai_compatible` in [llm/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/llm/service.py:81). |
| A5 | PASS | `try_upsert_property_embedding` wraps failures in `try/except` and logs warnings only in [embeddings/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/embeddings/service.py:50). |
| A6 | PASS | Missing `EMBEDDING_API_KEY` or `LLM_API_KEY` returns HTTP 503 in [ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:186). |
| A7 | PASS | Query-parsing failures are caught and returned as `query_parsed=False` in [ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:194). |
| A8 | PASS | Semantic failure falls back to pure filter search via `return filter_ids` in [ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:177). |
| A9 | PASS | `POST /api/v1/search/ai` exists and is login-gated with `get_current_user` in [ai_search/router.py](/home/lecherme/workspace/vibe-home/backend/app/api/v1/ai_search/router.py:12). |
| A10 | PASS | `POST /api/v1/admin/embeddings/sync` exists and is admin-gated in [admin/router.py](/home/lecherme/workspace/vibe-home/backend/app/api/v1/admin/router.py:42). |
| A11 | PASS | `create_property` and `update_property` call `try_upsert_property_embedding` before return in [admin/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/admin/service.py:33). |
| A12 | PASS | `docker compose exec backend python -c "import app.main; print('OK')"` exited 0. |
| A13 | PASS | `AiSearchRequest` and `AiSearchResult` are published in [frontend/types/search.ts](/home/lecherme/workspace/vibe-home/frontend/types/search.ts:19). |
| A14 | PASS | `aiSearch()` and status-carrying `AiSearchApiError` exist in [frontend/lib/api/ai-search.ts](/home/lecherme/workspace/vibe-home/frontend/lib/api/ai-search.ts:5). |
| A15 | PASS | `AiSearchBar` has input + button, Enter handling, loading disable, and explicit Tailwind button colors in [ai-search-bar.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/ai-search-bar.tsx:11). |
| A16 | PASS | `AiParsedFiltersCard` shows the fallback message for `queryParsed=false`, chips for parsed filters, and summary in [ai-parsed-filters-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/ai-parsed-filters-card.tsx:10). |
| A17 | PASS | `/search` has both `Filter Search` and `✨ AI Search` modes in [page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:175). |
| A18 | PASS | AI-mode error banner is implemented in [page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:262). |
| A19 | PASS | AI-mode empty state is implemented in [page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:355). |
| A20 | PASS | Filter-search mode remains intact and separate from AI mode in [page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:198). |
| A21 | PASS | `cd frontend && npx tsc --noEmit` exited 0. |
| A22 | PASS | Static review confirms the tab toggle and preserved filter-search branch in [page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:175); live UX check remains for T04. |
| A23 | PASS | Static implementation covers NL query -> backend AI result -> parsed-filters card + summary through [ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:186) and [page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:228); live provider-backed validation remains for T04. |
| A24 | PASS | Missing-key behavior is wired end-to-end: backend 503 in [ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:186) and frontend AI error banner in [page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:262). |
| Scope: boundary compliance | PASS | No unauthorized source-file changes are evident from the recorded T01/T02 file lists; current worktree diff only touches review-control files. |
| Scope: `status.json` ownership | PASS | `status.json` is modified, but the diff and activity log entries are attributed to Claude runtime updates in [status.json](/home/lecherme/workspace/vibe-home/.ai/features/F15-hybrid-ai-search/status.json:61). |
| Frontend business logic | PASS | Search parsing, embedding, merge, fallback, and summary logic remain backend-side in [ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:145); frontend code is API orchestration/presentation only in [page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:132). |

## Issues Found
- WARNING: `parsed_filters` is typed in the frontend as optional-only fields in [frontend/types/search.ts](/home/lecherme/workspace/vibe-home/frontend/types/search.ts:3), but the backend response model uses nullable fields in [backend/app/schemas/search.py](/home/lecherme/workspace/vibe-home/backend/app/schemas/search.py:6). The runtime null-handling fix avoids the immediate UI bug, but the published TS contract is still looser than the actual API payload.
- WARNING: `POST /api/v1/admin/embeddings/sync` returns `{"synced": len(properties)}` in [backend/app/api/v1/admin/router.py](/home/lecherme/workspace/vibe-home/backend/app/api/v1/admin/router.py:48) even when individual upserts fail and are only logged. The endpoint reports attempted count, not successful count.
- WARNING: No automated tests were added for the new AI search, embeddings, LLM provider dispatch, or frontend AI mode flows. The current verification is limited to import/TypeScript checks.

## Required Fixes
- None.

## Approved Items
- Backend provider abstraction, embedding service, AI search service, router registration, and admin embedding hooks are implemented and wired correctly.
- Frontend AI search types, API client, search bar, parsed-filters card, tabbed integration, error banner, and empty state are implemented and type-check cleanly.
- `status.json` shows Claude-owned runtime bookkeeping only; no unauthorized Codex or Gemini modification was found.
- The required verification gates that were practical in review passed: backend import via Docker and frontend `tsc --noEmit`.
