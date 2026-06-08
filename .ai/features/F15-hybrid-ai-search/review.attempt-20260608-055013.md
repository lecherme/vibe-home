# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | [backend/migrations/003_create_property_embeddings.sql](/home/lecherme/workspace/vibe-home/backend/migrations/003_create_property_embeddings.sql:1) contains the vector extension, `property_embeddings`, and `match_property_embeddings`. |
| A2 | PASS | `openai` and `anthropic` are present in [backend/requirements.txt](/home/lecherme/workspace/vibe-home/backend/requirements.txt:11). |
| A3 | PASS | New `LLM_*` and `OPENAI_API_KEY` fields exist in [backend/app/core/config.py](/home/lecherme/workspace/vibe-home/backend/app/core/config.py:18); `ANTHROPIC_*` fields are absent. |
| A4 | PASS | `embed_text`, `try_upsert_property_embedding`, and `semantic_search` exist in [backend/app/services/embeddings/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/embeddings/service.py:33). |
| A4b | PASS | `complete(prompt, max_tokens, temperature)` exists and branches for `anthropic`, `openai`, and `openai_compatible` in [backend/app/services/llm/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/llm/service.py:81). |
| A5 | PASS | `try_upsert_property_embedding` wraps failures in `try/except` and logs warnings only in [backend/app/services/embeddings/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/embeddings/service.py:46). |
| A6 | PASS | Missing `OPENAI_API_KEY` or `LLM_API_KEY` returns HTTP 503 in [backend/app/services/ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:186). |
| A7 | PASS | Query parsing failures are caught and set `query_parsed=False` in [backend/app/services/ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:194). |
| A8 | PASS | Semantic-search failures fall back to pure filter search in [backend/app/services/ai_search/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/ai_search/service.py:158). |
| A9 | PASS | Authenticated `POST /api/v1/search/ai` exists in [backend/app/api/v1/ai_search/router.py](/home/lecherme/workspace/vibe-home/backend/app/api/v1/ai_search/router.py:12). |
| A10 | PASS | Admin-gated `POST /api/v1/admin/embeddings/sync` exists in [backend/app/api/v1/admin/router.py](/home/lecherme/workspace/vibe-home/backend/app/api/v1/admin/router.py:42). |
| A11 | PASS | `create_property` and `update_property` call `try_upsert_property_embedding` in [backend/app/services/admin/service.py](/home/lecherme/workspace/vibe-home/backend/app/services/admin/service.py:14). |
| A12 | PASS | `docker compose exec backend python -c "import app.main; print('OK')"` returned `OK`. |
| A13 | FAIL | Types are published in [frontend/types/search.ts](/home/lecherme/workspace/vibe-home/frontend/types/search.ts:19), but the contract is wrong: backend serializes `parsed_filters` fields as `null`, while frontend types model them as optional/`undefined` only. |
| A14 | PASS | `aiSearch()` and status-carrying `AiSearchApiError` exist in [frontend/lib/api/ai-search.ts](/home/lecherme/workspace/vibe-home/frontend/lib/api/ai-search.ts:5). |
| A15 | PASS | `AiSearchBar` has input + button, Enter trigger, loading disable, and explicit Tailwind button colors in [frontend/components/features/search/ai-search-bar.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/ai-search-bar.tsx:11). |
| A16 | FAIL | [frontend/components/features/search/ai-parsed-filters-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/ai-parsed-filters-card.tsx:15) treats `null` as a real value, so it can render chips like `$null - $null` / `null Beds` instead of correct parsed-filter output. |
| A17 | PASS | `/search` has both `"Filter Search"` and `"✨ AI Search"` modes in [frontend/app/(dashboard)/search/page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:175). |
| A18 | PASS | AI-mode error banner exists in [frontend/app/(dashboard)/search/page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:262). |
| A19 | PASS | AI-mode empty state exists in [frontend/app/(dashboard)/search/page.tsx](/home/lecherme/workspace/vibe-home/frontend/app/(dashboard)/search/page.tsx:355). |
| A20 | PASS | Existing filter-search path remains present; no source diff was found in the existing backend `/api/v1/properties/search` implementation. |
| A21 | PASS | `cd frontend && npx tsc --noEmit` exited 0. |
| A22 | PASS | Static review shows tab switching is implemented and filter mode remains intact; manual confirmation is deferred to T04. |
| A23 | FAIL | The AI result path is wired, but the parsed-filters card can display bogus filter chips when backend returns `null` fields, so the rendered parsed-filter output is not reliable. |
| A24 | PASS | Static review supports the error-banner path: backend returns 503 without keys and frontend surfaces API errors in AI mode. |
| Scope: `status.json` ownership | PASS | `status.json` is currently modified, but the diff/activity log attributes those state transitions to `claude`; no evidence shows Codex or Gemini edited it. |

## Issues Found
- BLOCKER: `parsed_filters` nullability is inconsistent across backend and frontend. Backend responses serialize missing filter fields as `null`, but [frontend/types/search.ts](/home/lecherme/workspace/vibe-home/frontend/types/search.ts:3) and [frontend/components/features/search/ai-parsed-filters-card.tsx](/home/lecherme/workspace/vibe-home/frontend/components/features/search/ai-parsed-filters-card.tsx:26) assume `undefined`, causing bogus chips such as `$null - $null`, `null Beds`, and `null Baths`.
- WARNING: `POST /api/v1/admin/embeddings/sync` always returns `{"synced": len(properties)}` in [backend/app/api/v1/admin/router.py](/home/lecherme/workspace/vibe-home/backend/app/api/v1/admin/router.py:48), even when `try_upsert_property_embedding` logs failures, so the reported sync count is not a true success count.
- WARNING: There is no automated coverage for the new AI search paths. No backend tests for AI parsing/semantic fallback or frontend tests for parsed-filter rendering/error states were added.

## Required Fixes
- Align the frontend AI search types with the backend wire format for `parsed_filters` and update `AiParsedFiltersCard` to ignore `null` values, not just `undefined`.
- Re-verify the AI parsed-filters UI with an empty/partial `parsed_filters` payload so it renders only real chips and the fallback copy remains correct.

## Approved Items
- Backend AI search, embeddings service, LLM abstraction, migration, router registration, and admin sync endpoint are present and wired.
- Required verifications passed for backend import and frontend `tsc --noEmit`.
- No boundary violation was found in the existing `/api/v1/properties/search` path.
- AI-specific business logic remains backend-side; the frontend additions are UI/API orchestration rather than domain logic.
