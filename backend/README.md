# Backend

FastAPI service for the `vibe_home` API.

## Environment Variables

Create `backend/.env` before running the service.

| Variable | Required | Purpose |
| --- | --- | --- |
| `SUPABASE_URL` | Yes | Supabase project URL used for persistence. |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Service role key used by the Supabase data client. |
| `SUPABASE_ANON_KEY` | Yes | Supabase anon key kept documented for parity with shared project configuration. |
| `SUPABASE_KEY` | Yes | Current backend auth compatibility variable; set this to the same value as `SUPABASE_SERVICE_ROLE_KEY`. |
| `SUPABASE_JWT_SECRET` | Yes | JWT secret used to validate Supabase-issued access tokens. |
| `ALLOWED_ORIGINS` | Yes | Comma-separated CORS allowlist, for example `http://localhost:3000`. |

## Docker Compose

`docker compose up --build` starts this service on `http://localhost:8000` and loads runtime configuration from `backend/.env`.

Copy `backend/.env.example` to `backend/.env` and provide real Supabase credentials before starting the stack.
