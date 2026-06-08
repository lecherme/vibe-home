# Review

## Verdict
PASS

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | Migration includes `vector`, `property_embeddings`, and `match_property_embeddings` in [003_create_property_embeddings.sql](/home/lecherme/workspace/vibe-home/backend/migrations/003_create_property_embeddings.sql:1). |
| A2 | PASS | `openai` and `anthropic` are present in [requirements.txt](/home/lecherme/workspace/vibe-home/backend/requirements.txt:11). |
| A3 | PASS | `OPENAI_API_KEY` and all `LLM_*` settings exist, with no `ANTHROPIC_*` remnants in [config.py](/home/lecherme/workspace/vibe-home/backend/app/core/config.py:18). |
| A4 | PASS | `embed_text`, `try_upsert_property_embedding`, and `semantic_search` exist in [embeddings/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/embeddings/service.py:33). |
| A4b | PASS | `complete(prompt, max_tokens, temperature)` supports `anthropic`, `openai`, and `openai_compatible` in [llm/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/llm/service.py:81). |
| A5 | PASS | `try_upsert_property_embedding` wraps failures in `try/except` and logs `warning` only in [embeddings/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/embeddings/service.py:46). |
| A6 | PASS | Missing `OPENAI_API_KEY` or `LLM_API_KEY` returns HTTP 503 in [ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:186). |
| A7 | PASS | Query-parsing failures are caught and return `query_parsed=False` in [ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:194). |
| A8 | PASS | Semantic-search failures fall back to pure filter search in [ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:177). |
| A9 | PASS | `POST /api/v1/search/ai` exists and is login-gated in [ai_search/router.py](/home/lecherme/workspace/vibe-home/backend/app/api/v1/ai_search/router.py:12). |
| A10 | PASS | `POST /api/v1/admin/embeddings/sync` exists and is admin-gated in [admin/router.py](/home/lecherme/workspace/vibe-home/backend/app/api/v1/admin/router.py:42). |
| A11 | PASS | `create_property` and `update_property` call `try_upsert_property_embedding` before return in [admin/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/admin/service.py:33). |
| A12 | PASS | Verified with `docker compose exec backend python -c "import app.main; print('OK')"`; exit 0. |
| A13 | PASS | `AiSearchRequest` and `AiSearchResult` are exported from [frontend/types/search.ts](/home/lecherme/workspace/vibe-home/frontend/types/search.ts:19). |
| A14 | PASS | `aiSearch()` and `AiSearchApiError.status` exist in [frontend/lib/api/ai-search.ts](/home/lecherme/workspace/vibe-home/frontend/lib/api/ai-search.ts:5). |
| A15 | PASS | `AiSearchBar` has input + button, Enter submit, loading disable, and explicit Tailwind button colors in [ai-search-bar.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/ai-search-bar.tsx:11). |
| A16 | PASS | `AiParsedFiltersCard` shows fallback text on `queryParsed=false` and chips + summary on success in [ai-parsed-filters-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/ai-parsed-filters-card.tsx:84). |
| A17 | PASS | `/search` has parallel `Filter Search` and `✨ AI Search` modes in [page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:175). |
| A18 | PASS | AI mode renders an error banner in [page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:262). |
| A19 | PASS | AI mode renders an empty state in [page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:355). |
| A20 | PASS | Existing filter-search flow remains in place in [page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:198), and no change was found in the existing `/api/v1/properties/search` path. |
| A21 | PASS | Verified with `npx tsc --noEmit`; exit 0. |
| Frontend business logic | PASS | Hybrid parsing/merge/fallback logic stays in backend services; frontend additions are UI state and API calls only. |
| `status.json` ownership | PASS | `status.json` is modified in the worktree, but the diff and activity log show Claude runtime updates only; no evidence of Codex or Gemini edits. |
| API types published | PASS | The AI request/result types are published from [frontend/types/search.ts](/home/lecherme/workspace/vibe-home/frontend/types/search.ts:19). |

## Issues Found
- WARNING: The broader spec fallback contract is only partially implemented. On embedding/semantic failure, `ai_search()` keeps `query_parsed=True` and returns pure filter results; with empty filters that becomes the full property set rather than keyword fallback. See [backend/app/services/ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:154) and [backend/app/services/ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:177).
- WARNING: `POST /api/v1/admin/embeddings/sync` returns `{"synced": len(properties)}` even when individual upserts fail, so the response is an attempt count, not a success count. See [backend/app/api/v1/admin/router.py](/home/lecherme/workspace/vibe-home/backend/app/api/v1/admin/router.py:48).
- WARNING: No automated tests were added for the new embeddings, LLM, AI-search, or AI-search UI paths, leaving the fallback behavior largely unguarded.

## Required Fixes
- None.

## Approved Items
- Multi-provider LLM configuration and dispatch are wired correctly.
- Embedding upserts are best-effort and do not break property create/update flows.
- The AI search endpoint, admin sync endpoint, and frontend AI tab are all correctly integrated.
- No boundary violation was found in the existing `/api/v1/properties/search` flow.
- No unauthorized Codex/Gemini modification of `status.json` was found.
