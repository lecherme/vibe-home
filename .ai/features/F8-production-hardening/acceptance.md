# Production Hardening — Acceptance Criteria

T05 (Codex review) verifies every criterion below and writes `review.md`.
T06 (Claude acceptance) reads `review.md` and writes `final-report.md`.

---

## Criteria

| # | Criterion | Check |
|---|-----------|-------|
| A1 | CORS `allow_origins`, `allow_methods`, and `allow_headers` in `CORSMiddleware` use explicit allowlists (no `*`); `CORS_ALLOWED_ORIGINS` env var documented in `backend/.env.example`; CORS preflight for a disallowed method returns 400/403 | Read `backend/app/main.py`; grep for `*` wildcard in CORS config; read `.env.example` |
| A2 | **架构说明：** signIn/signUp 由前端直连 Supabase，后端无真实 POST auth 端点；rate limiting 施加于后端唯一真实认证端点 `GET /api/v1/auth/me`。验收：(1) `GET /api/v1/auth/me` 有 `@auth_rate_limiter.limit` 装饰器且接受 `request: Request` 参数；(2) 连续超限请求返回 429；(3) 虚构的 `POST /api/v1/auth/me` 端点不存在；(4) `RATE_LIMIT_AUTH` 已文档化；(5) `pytest backend/tests/test_rate_limiting.py` 退出码为 0 | 读 `backend/app/api/v1/auth/router.py` 确认 GET /me 有装饰器且无 POST /me；运行 pytest |
| A3 | Backend logs are valid JSON Lines at runtime; each log line contains at minimum `level`, `timestamp`, `message`, `request_id` keys; structured logging configured at app startup | Read logging setup in `main.py` (or `core/logging.py`); verify JSON handler and request_id middleware are wired |
| A4 | `DELETE /api/v1/admin/properties/{id}` removes all associated `favorites` rows; affected users' favorites list no longer includes the deleted property; test covers cascade and exits 0 | Read `backend/app/services/admin/service.py`; run relevant pytest test |

---

## Review and Acceptance

If review verdict is FAIL, Claude does NOT proceed directly to T06 acceptance.
Claude must:
1. Write `last_review_failure` to `status.json` with `fix_path`, `failed_criteria`, and `fix_instructions`.
2. Choose fix_path: `task_retry`, `direct_fixup`, or `review_rerun`.
3. Apply the fix and re-run review before acceptance.

## Rejection Conditions

- Any task modifies files outside its declared Scope in `tasks.md`.
- Any worker modifies `status.json`.
- Any required artifact is missing or malformed.
- CORS config retains a wildcard `*` for origins, methods, or headers.
- `GET /api/v1/auth/me` 没有 rate limiting 装饰器。
- `POST /api/v1/auth/me` 合成端点仍然存在于 `auth/router.py`（该端点非真实业务路由，必须删除）。
- Log output is not valid JSON Lines.
- Property deletion does not cascade to favorites.
