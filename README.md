# vibe_home

`vibe_home` is a two-service foundation for a Next.js frontend and a FastAPI backend. The backend currently exposes a single `GET /health` endpoint, and the frontend includes a minimal health page that fetches that endpoint and displays the response.

## Prerequisites

- Node.js 18 or newer
- Python 3.11 or newer

## Backend Setup

1. Copy the example environment file:

```bash
cd backend
cp .env.example .env
```

2. Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run the backend development server:

```bash
uvicorn app.main:app --reload
```

The backend reads these environment variables from `backend/.env`:

- `SUPABASE_URL`
- `SUPABASE_KEY`
- `ALLOWED_ORIGINS`

## Frontend Setup

1. Copy the example environment file:

```bash
cd frontend
cp .env.example .env.local
```

2. Install dependencies:

```bash
npm install
```

3. Run the frontend development server:

```bash
npm run dev
```

The frontend reads `NEXT_PUBLIC_API_URL` from `frontend/.env.local`. For local development, the example value points to `http://localhost:8000`.

## Verify The Setup

1. Start the backend and open `http://localhost:8000/health`. The response should be:

```json
{"status":"ok"}
```

2. Start the frontend and open `http://localhost:3000`. The health page should fetch the backend `GET /health` endpoint and display the returned status.
