# F15 Acceptance Criteria

## Backend (T01)

| ID | Criterion |
|----|-----------|
| A1 | migration SQL 文件存在，包含 vector extension、property_embeddings 表、match_property_embeddings RPC |
| A2 | `openai` 和 `anthropic` 在 requirements.txt |
| A3 | config.py 有 EMBEDDING_API_KEY / EMBEDDING_MODEL / EMBEDDING_BASE_URL / LLM_PROVIDER / LLM_API_KEY / LLM_MODEL / LLM_BASE_URL 字段；无 OPENAI_API_KEY / ANTHROPIC_API_KEY / ANTHROPIC_MODEL |
| A4 | embedding service：embed_text / try_upsert_property_embedding / semantic_search 均存在 |
| A4b | llm service：complete(prompt, max_tokens, temperature) 存在；支持 anthropic / openai / openai_compatible provider |
| A5 | try_upsert_property_embedding 有 try/except，失败只 log warning |
| A6 | ai_search service 在 EMBEDDING_API_KEY 或 LLM_API_KEY 缺失时返回 HTTP 503 |
| A7 | ai_search 的 LLM query parsing 失败时 query_parsed=False，不抛异常 |
| A8 | ai_search 的 semantic_search 失败时退回纯 filter 搜索 |
| A9 | POST /api/v1/search/ai 端点存在，需登录 |
| A10 | POST /api/v1/admin/embeddings/sync 端点存在，admin-gated |
| A11 | create_property / update_property 末尾调用 try_upsert_property_embedding |
| A12 | `python -c "import app.main"` exit 0 |

## Frontend (T02)

| ID | Criterion |
|----|-----------|
| A13 | AiSearchResult / AiSearchRequest 类型在 types/search.ts |
| A14 | aiSearch() 函数在 lib/api/ai-search.ts，错误带 status |
| A15 | AiSearchBar 组件：Input + Button，Enter 触发，isLoading 禁用，Button 显式 Tailwind 颜色 |
| A16 | AiParsedFiltersCard：queryParsed=false 时显示 fallback 文字；queryParsed=true 时显示 filter chips + summary |
| A17 | /search 页有 "Filter Search" / "✨ AI Search" tab，两个 mode 并存 |
| A18 | AI mode 错误时显示 error banner |
| A19 | AI mode 无结果时显示空状态文字 |
| A20 | 现有 Filter Search 功能无退化 |
| A21 | tsc --noEmit exit 0 |

## Manual (T04 Claude)

| ID | Criterion |
|----|-----------|
| A22 | AI Search tab 可切换，Filter Search 仍正常工作 |
| A23 | 输入自然语言 query → 返回结果 + parsed filters 卡片 + summary（keys 已配置时） |
| A24 | Fallback：keys 未配置时显示 error banner（不崩溃） |
