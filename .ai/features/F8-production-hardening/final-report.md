# F8 Production Hardening — Final Report

## Disposition: ACCEPTED

## Review Summary

T05 (Codex review, retry-1) verdict: **PASS** — all four acceptance criteria satisfied.

| Criterion | Result | Summary |
|-----------|--------|---------|
| A1 — CORS hardening | PASS | `CORSMiddleware` 使用明确 allowlist，无 `*` 通配符；`CORS_ALLOWED_ORIGINS` 已文档化；disallowed method preflight 返回 400 |
| A2 — Rate limiting | PASS | `GET /api/v1/auth/me` 施加 `@auth_rate_limiter.limit`；无虚构 `POST /auth/me`；`RATE_LIMIT_AUTH` 已文档化；`slowapi` 死重依赖已移除；`pytest test_rate_limiting.py` 1 passed |
| A3 — Structured JSON logging | PASS | JSON Lines 格式，含 `level`/`timestamp`/`message`/`request_id` 四个必填字段；`request_id` 由 per-request UUID 中间件注入；运行时 probe 验证通过 |
| A4 — Cascade delete favorites | PASS | `delete_property()` 先删 favorites 行再删 property 行；`pytest test_admin_properties.py` 18 passed；favorites 列表不再暴露已删除的 property |

## Scope Notes

- **A2 架构校正（已记录）：** F8 原始 spec 假设后端有 `POST /api/v1/auth/*` 登录端点，但实际架构中 signIn/signUp 由前端直连 Supabase，后端不存在此类端点。经确认，rate limiting 目标校正为后端唯一真实认证端点 `GET /api/v1/auth/me`，spec/tasks/acceptance 均已同步更新。此校正属于架构现实对齐，非需求降级。
- 所有实现文件均在 T01–T04 声明 scope 内；无 boundary violation。
- `status.json` 全程仅由 claude 修改，无 Codex/Gemini 越权记录。
- 本 feature 无新 backend schema 类型，无需向 `frontend/types/` 发布。

## Known Non-Blocking Issues

- `@app.on_event("startup")` 在 FastAPI 新版中已弃用，运行时会产生 deprecation warning。功能不受影响，建议在后续维护周期迁移至 `lifespan` 模式，不阻断本次 acceptance。

## Deliverables Verified

- `backend/app/main.py` — CORS hardening + request_id 中间件 + logging 初始化
- `backend/app/core/logging.py` — JSON Lines formatter + ContextVar request_id 传播
- `backend/app/api/v1/auth/router.py` — `AuthRateLimiter` + rate limit 施加于 `GET /api/v1/auth/me`
- `backend/app/services/admin/service.py` — 级联删除 favorites
- `backend/tests/test_rate_limiting.py` — rate limiting 测试（GET /auth/me，429 验证）
- `backend/tests/test_admin_properties.py` — 级联删除测试（18 passed）
- `backend/.env.example` — `CORS_ALLOWED_ORIGINS`、`RATE_LIMIT_AUTH` 已文档化
- `backend/requirements.txt` — `slowapi` 死重依赖已移除
