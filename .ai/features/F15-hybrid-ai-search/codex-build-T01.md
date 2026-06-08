# Codex Build Report

## Task Completed
- T01

## Files Changed
- backend/app/core/config.py
- backend/app/services/embeddings/service.py
- backend/app/services/ai_search/service.py

## API Types Published
- None

## Tests Written
- None

## Open Issues
- `backend/tests/test_embeddings_service.py` was not added because `backend/tests/` is outside the T01 allowed file list, so service-layer test coverage for the new AI search/embedding code remains incomplete in this scoped fixup.
- `backend/tests/test_llm_service.py` was not added because `backend/tests/` is outside the T01 allowed file list, so service-layer test coverage for LLM provider dispatch remains incomplete in this scoped fixup.
- `backend/tests/test_ai_search_service.py` was not added because `backend/tests/` is outside the T01 allowed file list, so service-layer test coverage for AI search fallback behavior remains incomplete in this scoped fixup.
- `backend/migrations/003_create_property_embeddings.sql` still uses `vector(1536)` per T01 acceptance, while the feature spec text also mentions default `embedding-3` as 2048 dimensions; the runtime fixup did not authorize a schema change, so the configured embedding model/provider must remain compatible with 1536 dimensions until that spec conflict is resolved.
