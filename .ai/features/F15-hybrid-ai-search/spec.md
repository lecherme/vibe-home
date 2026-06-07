# F15 — Hybrid AI Search V1

**Status:** in_progress
**Created:** 2026-06-07

## Goal

在现有结构化搜索基础上叠加 AI 能力：用户输入自然语言 query → Claude 解析结构化 filters → OpenAI embedding + pgvector 语义检索 → 现有 filter pipeline 兜底 → Claude 生成一行 summary。

## Architecture

```
User NL query
    ↓
Claude (query parsing) → structured filters (location/price/beds/baths/status)
    ↓ (parallel)
OpenAI embedding → pgvector similarity search → top-N semantic candidates
    ↓
Hybrid merge: semantic candidates ∩ structured filters
    ↓ (fallback if <threshold)
Supplement with pure filter search on all properties
    ↓
Paginate → Claude summary (one sentence)
    ↓
Frontend: parsed filters card + result grid + summary
```

## Scope

### V1 必做
- `property_embeddings` 表（pgvector）+ `match_property_embeddings` RPC（migration 文件编号在实际创建时定）
- Admin 端 embedding sync utility：`POST /api/v1/admin/embeddings/sync`（best-effort，批量为现有房源生成 embedding，失败的 property 跳过并 log）
- create_property / update_property 后自动 upsert embedding（best-effort，失败记 warning log，不影响主流程）
- AI search endpoint：`POST /api/v1/search/ai`
- 前端：/search 页新增 AI Search tab；AI parsed filters 展示卡片；AI summary 展示；fallback 提示
- Fallback：OpenAI / Claude 任一失败 → 退回普通关键词搜索，返回 `query_parsed: false`

### V1 不做
- 复杂 rerank 策略（semantic score × filter score 加权）
- 后台定时重建 embedding
- 可编辑 parsed filters 卡片
- 历史搜索、推荐、解释面板
- streaming response

## Key Tech Decisions

- **Embeddings model**: `text-embedding-3-small`（1536 dims）
- **Embedding text**: `"{title}. {description}. Located in {location}."` per property
- **Claude model**: 通过 env `ANTHROPIC_MODEL` 配置，默认用轻量 Claude model（query parsing 不需要 Opus）
- **Vector search**: Supabase pgvector RPC `match_property_embeddings`，返回 top-50 candidates
- **Hybrid threshold**: 若语义候选经 filter 后 < 5 条，补充纯 filter 结果（union）

## Constraints

- `tsc --noEmit` 通过
- `python -c "import app.main"` 通过
- AI search endpoint 在 `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` 缺失时返回 HTTP 503
- create_property / update_property embedding 失败时记 warning log，不抛异常
- 不修改现有 `/api/v1/properties/search` endpoint 行为
- migration 文件需人工在 Supabase Dashboard 执行（T01 产出 SQL，不自动执行）
