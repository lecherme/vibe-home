# F15 Hybrid AI Search V1 — Tasks

---

## T01 — Codex: Backend

- **owner:** codex
- **type:** build
- **depends_on:** none
- **allowed files:** see owner.md T01

### Migration SQL

在 `backend/migrations/` 下新建下一个可用编号的 SQL 文件，内容包含：
- `CREATE EXTENSION IF NOT EXISTS vector`
- `property_embeddings` 表：`property_id TEXT PK`、`embedding vector(1536)`、`updated_at TIMESTAMPTZ`
- RPC 函数 `match_property_embeddings(query_embedding vector(1536), match_count int)`，按余弦距离升序返回 `(property_id text, similarity float)`，默认 50 条

文件只产出，不自动执行（人工 Supabase Dashboard 执行）。

### Dependencies

`backend/requirements.txt` 追加 `openai` 和 `anthropic`（使用当前稳定版本）。

### Config

`backend/app/core/config.py` Settings 类增加以下字段：
- `EMBEDDING_API_KEY`（可选，embedding 调用凭证）
- `EMBEDDING_MODEL`（默认 `"embedding-3"`）
- `EMBEDDING_BASE_URL`（可选，默认 `"https://open.bigmodel.cn/api/paas/v4/"`）
- `LLM_PROVIDER`（默认 `"anthropic"`，可选值：`anthropic` | `openai` | `openai_compatible`）
- `LLM_API_KEY`（可选，LLM 调用凭证）
- `LLM_MODEL`（有默认值，使用轻量 Claude 型号）
- `LLM_BASE_URL`（可选，仅 `openai_compatible` provider 需要）

移除原有的 `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `ANTHROPIC_MODEL` 字段。

### Embedding service

新建 `backend/app/services/embeddings/service.py`，需提供：
- `embed_text(text: str) -> list[float]`：用 OpenAI SDK + `EMBEDDING_API_KEY` / `EMBEDDING_MODEL` / `EMBEDDING_BASE_URL` 调用 embedding endpoint，返回向量
- `try_upsert_property_embedding(property_id, title, description, location) -> None`：best-effort，内部 try/except，失败只 log warning，绝不抛异常
- `semantic_search(query_embedding, match_count=50) -> list[str]`：调用 `match_property_embeddings` RPC，返回 property_id 列表

### LLM service

新建 `backend/app/services/llm/service.py`，提供 `complete(prompt: str, max_tokens: int, temperature: float) -> str`：

**行为要求：**
- 读取 `settings.llm_provider`，按以下路径分发：
  - `anthropic` → 使用 Anthropic SDK，`api_key=settings.llm_api_key`
  - `openai` → 使用 OpenAI SDK，`api_key=settings.llm_api_key`
  - `openai_compatible` → 使用 OpenAI SDK，`api_key=settings.llm_api_key`，`base_url=settings.llm_base_url`
  - 未知 provider → 抛 `RuntimeError`
- 返回纯字符串（stripped），不返回 SDK 原始对象

### AI search service

新建 `backend/app/services/ai_search/service.py`，提供 `ai_search(query, page, page_size) -> AiSearchResult`：

**行为要求：**
1. `EMBEDDING_API_KEY` 或 `LLM_API_KEY` 任一缺失时抛 `HTTPException(503)`
2. 调用 LLM service（`complete()`）从 query 解析结构化 filters（location/min_price/max_price/bedrooms/bathrooms/status），失败时返回空 filters，`query_parsed=False`
3. 调用 OpenAI embed query → pgvector `semantic_search`，失败时跳过语义步骤
4. Hybrid merge：语义候选 ∩ 结构化 filters；若结果 < 5 条，用纯 filter search 补充（union，去重）
5. 若无语义结果且 filters 为空，用 query 做关键词 fallback（title/location 包含）
6. 分页后调用 LLM service（`complete()`）生成一句 summary，失败时用 `"Found {total} properties matching your search."` 替代
7. 返回 `AiSearchResult`

### Schemas

新建 `backend/app/schemas/ai_search.py`：
```python
class AiSearchRequest(BaseModel):
    query: str
    page: int = 1
    page_size: int = 20

class AiSearchResult(SearchResult):   # 继承现有 SearchResult
    parsed_filters: SearchFilters
    ai_summary: str
    query_parsed: bool
```

### API router

新建 `backend/app/api/v1/ai_search/router.py`：
- `POST /`（挂载后为 `/api/v1/search/ai`）
- 需登录（`get_current_user` 依赖）
- 接收 `AiSearchRequest`，返回 `AiSearchResult`

在 `backend/app/main.py` 注册该 router，prefix `/api/v1/search/ai`。

### Admin embedding sync

在 `backend/app/api/v1/admin/router.py` 新增 `POST /embeddings/sync`（admin-gated）：
- 遍历所有 properties，对每条调用 `try_upsert_property_embedding`
- 返回 `{"synced": <count>}`，status 202

### Embedding hooks

在 `backend/app/services/admin/service.py` 的 `create_property` 和 `update_property` 函数末尾（return 之前）调用 `try_upsert_property_embedding`。失败绝不影响主流程。

### Verification

```bash
docker compose exec backend python -c "import app.main; print('OK')"
```

---

## T02 — Gemini: Frontend AI Search UI

- **owner:** gemini
- **type:** build
- **depends_on:** T01
- **allowed files:** see owner.md T02

### Types

`frontend/types/search.ts` 追加：

```typescript
export interface AiSearchRequest {
  query: string;
  page?: number;
  page_size?: number;
}

export interface AiSearchResult extends SearchResult {
  parsed_filters: SearchFilters;
  ai_summary: string;
  query_parsed: boolean;
}
```

### API client

新建 `frontend/lib/api/ai-search.ts`：
- 导出 `aiSearch(query, page?, pageSize?): Promise<AiSearchResult>`
- `POST /api/v1/search/ai`，携带 Bearer token
- 抛出带 status 的自定义 error 类（参考 properties.ts 的 `PropertyApiError` 模式）

### Components

**`ai-search-bar.tsx`**：单行文本输入 + "AI Search" 按钮
- Enter 触发搜索
- `isLoading` 时禁用
- Button 颜色用显式 Tailwind class（`bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50`）

**`ai-parsed-filters-card.tsx`**：解析结果展示卡
- `queryParsed=false` 时显示 fallback 提示（"AI parsing unavailable — showing keyword results"）
- `queryParsed=true` 时展示解析出的 filters 以 chip 形式（location / price / beds / baths / status）
- 展示 `ai_summary`

### Search page integration

`frontend/app/(dashboard)/search/page.tsx` 新增 AI mode tab（"Filter Search" / "✨ AI Search"）：
- 两个 tab 切换，不删除任何现有 filter search 逻辑
- AI mode：`AiSearchBar` + 结果区（`AiParsedFiltersCard` + `PropertyCard` grid）
- 错误时显示 error banner
- 无结果时显示空状态文字
- AI mode 不做 URL params sync（V1 不需要）

### Verification

```bash
docker compose exec frontend npx tsc --noEmit
```

---

## T03 — Codex: review

- **owner:** codex
- **type:** review
- **depends_on:** T01, T02

Review against acceptance.md criteria。只读，不修改源文件。

---

## T04 — Claude: acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T03
