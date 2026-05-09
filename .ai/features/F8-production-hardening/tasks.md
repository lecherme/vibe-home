# Production Hardening — Tasks

Every task has exactly one owner. Collaboration happens through sequential tasks, not shared tasks.

---

## T01 — CORS hardening

- **owner:** codex
- **type:** build
- **depends_on:** none

**Scope:**
- `backend/app/main.py` — replace wildcard `*` in `CORSMiddleware` with explicit `allow_origins`, `allow_methods`, `allow_headers` allowlists read from env var `CORS_ALLOWED_ORIGINS`
- `backend/.env.example` — add `CORS_ALLOWED_ORIGINS` with an example value

**Done condition:** `CORSMiddleware` no longer uses `*` for origins, methods, or headers; `CORS_ALLOWED_ORIGINS` env var is documented in `backend/.env.example`; CORS preflight for a disallowed method returns 400/403. Artifact: `codex-build-T01.md`.

---

## T02 — Auth rate limiting

- **owner:** codex
- **type:** build
- **depends_on:** T01

**架构说明：** signIn / signUp 由前端直连 Supabase，后端不存在真实的 `POST /api/v1/auth/*` 端点。Rate limiting 施加于后端唯一真实认证端点 `GET /api/v1/auth/me`。

**Scope:**
- `backend/app/api/v1/auth/router.py` — 在 `GET /api/v1/auth/me` 端点上施加 `@auth_rate_limiter.limit(get_auth_rate_limit)` 装饰器；为该端点添加 `request: Request` 参数；**删除** 虚构的 `POST /api/v1/auth/me` 端点（该端点无真实业务调用方）
- `backend/requirements.txt` — **移除** `slowapi`（自定义 `AuthRateLimiter` 未使用该库，属于死重依赖）
- `backend/.env.example` — 确认 `RATE_LIMIT_AUTH` 已文档化（已由上次执行写入，仅核查）
- `backend/tests/test_rate_limiting.py` — 将测试从 `POST /api/v1/auth/me` 改为 `GET /api/v1/auth/me`；连续超过配置次数请求后断言返回 429

**Done condition:** 连续超过配置次数向 `GET /api/v1/auth/me` 发起请求返回 429；`POST /api/v1/auth/me` 合成端点已删除；`RATE_LIMIT_AUTH` 已文档化；`pytest backend/tests/test_rate_limiting.py` 退出码为 0。Artifact: `codex-build-T02.md`.

---

## T03 — Structured JSON logging

- **owner:** codex
- **type:** build
- **depends_on:** T01

**Scope:**
- `backend/app/main.py` (or `backend/app/core/logging.py` if extracted) — configure Python `logging` at app startup to emit JSON Lines; each line must be a valid JSON object with at minimum: `level`, `timestamp`, `message`, `request_id`
- Middleware to inject a `request_id` (UUID) per request and propagate it to the log formatter
- No changes to existing `logger.info(...)` / `logger.error(...)` call sites required

**Done condition:** Application startup configures a JSON logging handler; a sample log line is valid JSON containing `level`, `timestamp`, `message`, `request_id` keys; existing tests still pass. Artifact: `codex-build-T03.md`.

---

## T04 — Cascade delete favorites

- **owner:** codex
- **type:** build
- **depends_on:** T01

**Scope:**
- `backend/app/services/admin/service.py` — in the `delete_property` method, before (or atomically with) deleting the `properties` row, delete all `favorites` rows where `property_id` matches
- `backend/tests/test_admin_properties.py` — add or update test to assert that after a property is deleted, no favorites rows for that `property_id` remain

**Done condition:** Deleting a property via `DELETE /api/v1/admin/properties/{id}` removes all associated favorites rows; test covers cascade behavior and exits 0. Artifact: `codex-build-T04.md`.

---

## T05 — Codex review

- **owner:** codex
- **type:** review
- **depends_on:** T02, T03, T04

**Scope:**
- Validate all deliverables against `acceptance.md` criteria A1–A4.
- Check ownership boundaries and file scope per task.
- Write `review.md`.

**Done condition:** `review.md` written with verdict (PASS/FAIL), per-criterion results A1–A4, and enough failure detail for Claude to choose `task_retry`, `direct_fixup`, or `review_rerun`.

---

## T06 — Claude acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T05

**Scope:**
- Read `review.md`.
- Write `final-report.md` with disposition `accepted` or `failed`.
- Update `status.json` feature status to `done` or `failed`.

**Done condition:** `final-report.md` written and `status.json` updated.
