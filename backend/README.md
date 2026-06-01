# Backend

FastAPI service for the `vibe_home` API.

## Environment Variables

Create `backend/.env` before running the service.

| Variable | Required | Purpose |
| --- | --- | --- |
| `SUPABASE_URL` | Yes | Supabase project URL used for persistence and JWKS endpoint. |
| `SUPABASE_KEY` | Yes | The Supabase key the backend client uses. Set to the **service role key** in production. |
| `SUPABASE_SERVICE_ROLE_KEY` | Reference only | Documented for shared project parity; not directly read by the backend client. |
| `SUPABASE_ANON_KEY` | Reference only | Documented for shared project parity; not directly read by the backend client. |
| `SUPABASE_JWT_SECRET` | No | Optional. Retained for reference. JWT verification uses Supabase JWKS (ES256) — this value is not used by the backend. |
| `CORS_ALLOWED_ORIGINS` | Production | Comma-separated CORS allowlist. **Takes priority over `ALLOWED_ORIGINS` when set.** Recommended for production, e.g. `https://yourdomain.com`. |
| `ALLOWED_ORIGINS` | Yes | Comma-separated CORS allowlist. Used as fallback when `CORS_ALLOWED_ORIGINS` is not set. Required by the config parser. |
| `RATE_LIMIT_AUTH` | No | Rate limit for auth endpoints. Default: `5/minute`. Format: `<count>/<second\|minute\|hour\|day>`. |

## Docker Compose

`docker compose up --build` starts this service on `http://localhost:8000` and loads runtime configuration from `backend/.env`.

Copy `backend/.env.example` to `backend/.env` and provide real Supabase credentials before starting the stack.
