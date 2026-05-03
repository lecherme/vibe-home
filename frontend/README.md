# Frontend

Next.js application for the `vibe_home` client.

## Environment Variables

Create `frontend/.env` before running the service.

| Variable | Required | Purpose |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | Yes | Public backend base URL, for local Docker Compose use `http://localhost:8000`. |
| `NEXT_PUBLIC_SUPABASE_URL` | Yes | Supabase project URL exposed to the browser and server runtime. |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | Supabase anon key exposed to the browser and server runtime. |

`frontend/.env` is read during the Docker image build, so these values must exist before `docker compose up --build`.

## Docker Compose

`docker compose up --build` starts this service on `http://localhost:3000` after the backend health check passes.
