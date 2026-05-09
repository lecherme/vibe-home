# Production Hardening

## Goal

Harden the running system for production traffic: restrict CORS to explicit origin allowlists, add rate limiting on auth endpoints, introduce structured JSON logging, and fix the orphaned-favorites bug triggered by property deletion.

## Scope

### Backend — CORS hardening
- `backend/app/main.py` (or wherever `CORSMiddleware` is configured) — restrict `allow_origins`, `allow_methods`, and `allow_headers` to explicit allowlists; remove wildcard `*` from all three fields
- `backend/.env.example` — document `CORS_ALLOWED_ORIGINS` env var

### Backend — Rate limiting

**架构说明：** 本项目的 `signIn` / `signUp` / `signOut` 由前端通过 Supabase JS 客户端直连 Supabase 服务器处理，流量不经过本后端。后端不存在真实的 `POST /api/v1/auth/*` 登录/注册端点。

因此 rate limiting 目标校正为后端唯一真实的认证相关端点：
- 对 `GET /api/v1/auth/me`（JWT 验证 + 返回当前用户）施加 per-IP rate limiting
- 目的：防止高频 JWT 轮询/暴力验证攻击
- Rate limit 配置通过 `RATE_LIMIT_AUTH` 环境变量控制（格式如 `5/minute`）
- `backend/.env.example` — document `RATE_LIMIT_AUTH` env var

### Backend — Structured JSON logging
- Configure Python `logging` at app startup to emit JSON Lines (each log line is a valid JSON object containing at minimum: `level`, `timestamp`, `message`, `request_id`)
- `request_id` injected via middleware for each request
- No changes to existing log call sites required; handler-level formatting is sufficient

### Backend — Cascade delete favorites
- `DELETE /api/v1/admin/properties/{id}` — before (or atomically with) deleting the property row, delete all `favorites` rows where `property_id` matches
- Affected users' favorites lists must no longer include the deleted property

## Non-Goals

- Observability infrastructure (dashboards, alerting, Sentry, external log shipping)
- Database-level audit log
- Frontend error tracking
- Frontend UI changes of any kind
- Seed / sample data
- New user-facing features
- Multi-region or CDN configuration

## Constraints

- All implementation must follow `.ai/conventions.md` and `.ai/orchestration.md`.
- Workers must implement only their assigned task.
- `status.json` is updated only by Claude Code orchestration.
- No hardcoded URLs, keys, secrets, or IP allowlists in any source file.
- CORS origins must be runtime-configurable via env vars.

## Dependencies

- F7 (Production Persistence & Deployment) — must be `done`

## Required Env Vars

### Backend (new)
- `CORS_ALLOWED_ORIGINS` — comma-separated list of allowed origins (e.g. `http://localhost:3000,https://yourdomain.com`)
- `RATE_LIMIT_AUTH` — rate limit string for auth endpoints (e.g. `5/minute`)

All new vars must appear in `backend/.env.example`.
