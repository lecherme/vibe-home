# F15 Hybrid AI Search V1 — Ownership Boundaries

This is a static ownership map. Runtime state comes from `status.json`.

---

## T01（Codex）— Backend: pgvector + embeddings + AI search endpoint

**允许修改的文件：**
- `backend/requirements.txt`
- `backend/app/core/config.py`
- `backend/app/schemas/ai_search.py`（新建）
- `backend/app/services/embeddings/__init__.py`（新建）
- `backend/app/services/embeddings/service.py`（新建）
- `backend/app/services/llm/__init__.py`（新建）
- `backend/app/services/llm/service.py`（新建）
- `backend/app/services/ai_search/__init__.py`（新建）
- `backend/app/services/ai_search/service.py`（新建）
- `backend/app/api/v1/ai_search/__init__.py`（新建）
- `backend/app/api/v1/ai_search/router.py`（新建）
- `backend/app/main.py`（注册新 router）
- `backend/app/services/admin/service.py`（create_property / update_property 后 upsert embedding）
- `backend/app/api/v1/admin/router.py`（新增 POST /embeddings/sync）
- `backend/migrations/`（新建 migration SQL 文件，使用下一个可用编号）

**不得修改：** `frontend/`、`backend/app/api/v1/properties/`（现有 search endpoint）、`status.json`

**强制约束：**
- embedding upsert 必须 try/except，失败只 log warning，不能影响 create_property / update_property 主流程
- AI search endpoint 在 `OPENAI_API_KEY` / `LLM_API_KEY` 缺失时返回 HTTP 503
- 不修改现有 `/api/v1/properties/search` endpoint 或其 service

---

## T02（Gemini）— Frontend: AI Search UI

**允许修改的文件：**
- `frontend/types/search.ts`（扩展 AiSearchResult 类型）
- `frontend/lib/api/ai-search.ts`（新建）
- `frontend/components/features/search/ai-search-bar.tsx`（新建）
- `frontend/components/features/search/ai-parsed-filters-card.tsx`（新建）
- `frontend/app/(dashboard)/search/page.tsx`（添加 AI mode tab / toggle）

**不得修改：** `backend/`、`frontend/lib/auth/`、`frontend/components/ui/`、`status.json`

**强制约束：**
- AI mode 和现有 filter search mode 并列（tab 或 toggle），不替换现有功能
- Fallback（`query_parsed: false`）时显示明确的降级提示
- **Button 颜色显式写**：不依赖 shadcn CSS 变量

---

## T03（Codex）— Review

只读审查，不得修改任何源文件。

---

## T04（Claude）— Acceptance

Claude 写 `final-report.md` 并更新 `status.json`。

**允许修改的文件：**
- `.ai/features/F15-hybrid-ai-search/status.json`
- `.ai/features/F15-hybrid-ai-search/final-report.md`

---

## Boundary Rules（全阶段适用）

1. Workers 不得修改 `status.json`。
2. Workers 不得直接创建报告文件；harness 写入 artifact。
3. 现有 `/api/v1/properties/search` 不得改动。
4. embedding upsert 失败不能抛异常到上层。
5. migration SQL 只产出文件，不自动执行。
