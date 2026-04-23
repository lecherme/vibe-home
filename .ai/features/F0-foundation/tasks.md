# F0 — Tasks

Every task has exactly one owner. Collaboration happens through sequential tasks, not shared tasks.

---

## T01 — Backend skeleton

- **owner:** codex
- **type:** scaffold
- **depends_on:** none
- **title:** Initialize FastAPI backend with folder structure and health endpoint

**Scope:**
- Create `backend/` with the following structure:
  ```
  backend/
  ├── app/
  │   ├── api/v1/
  │   ├── core/
  │   │   └── config.py       # loads env vars via pydantic-settings
  │   ├── models/
  │   ├── schemas/
  │   ├── services/
  │   └── main.py             # FastAPI app, mounts router, CORS config
  ├── requirements.txt
  └── .env.example
  ```
- `GET /health` returns `{ "status": "ok" }`
- Supabase URL and key loaded from env in `core/config.py` (no live connection)
- `.env.example` documents: `SUPABASE_URL`, `SUPABASE_KEY`, `ALLOWED_ORIGINS`

**Done condition:** `uvicorn app.main:app` starts without errors; `GET /health` returns 200 with `{ "status": "ok" }`

---

## T02 — Frontend skeleton

- **owner:** codex
- **type:** scaffold
- **depends_on:** none
- **title:** Initialize Next.js frontend with Tailwind and shadcn

**Scope:**
- Create `frontend/` with Next.js App Router, Tailwind CSS, and shadcn/ui initialized
- Folder structure:
  ```
  frontend/
  ├── app/
  │   └── layout.tsx
  ├── components/
  │   ├── ui/                 # shadcn target dir (empty)
  │   └── features/           # feature components (empty)
  ├── lib/
  │   ├── api/                # typed fetch wrappers (empty)
  │   └── auth/               # auth helpers (empty)
  ├── types/                  # shared TS types (empty)
  └── .env.example
  ```
- `.env.example` documents: `NEXT_PUBLIC_API_URL`
- No pages yet beyond the default layout

**Done condition:** `next dev` starts without errors; no TypeScript or Tailwind config errors

---

## T03 — Health status page

- **owner:** gemini
- **type:** ui
- **depends_on:** T01, T02
- **title:** Scaffold minimal frontend health status page

**Scope:**
- Create `frontend/app/page.tsx` — a minimal page that:
  - Fetches `GET ${NEXT_PUBLIC_API_URL}/health` on load
  - Displays the response status (`ok` or error message)
  - No styling beyond basic Tailwind utility classes
- Page is purely presentational — no logic beyond the fetch and display
- Uses `NEXT_PUBLIC_API_URL` from env; falls back to `http://localhost:8000` if unset

**Done condition:** Page renders without errors; displays backend health response when backend is running; displays a clear error state when backend is unreachable

---

## T04 — Repo root README

- **owner:** codex
- **type:** docs
- **depends_on:** T01, T02
- **title:** Write root README with local setup instructions

**Scope:**
- Create `README.md` at repo root with:
  - Project overview (one paragraph)
  - Prerequisites (Node version, Python version)
  - Setup steps for backend: copy `.env.example`, install deps, run dev server
  - Setup steps for frontend: copy `.env.example`, install deps, run dev server
  - How to verify: visit health page, check `/health` endpoint

**Done condition:** README exists at repo root; setup steps are accurate and complete

---

## T05 — Codex review

- **owner:** codex
- **type:** review
- **depends_on:** T01, T02, T03, T04
- **title:** Review F0 implementation against acceptance criteria

**Scope:**
- Validate all T01–T04 deliverables against `acceptance.md`
- Check for boundary violations (business logic in frontend, hardcoded secrets, etc.)
- Write `review.md`

**Done condition:** `review.md` written with a verdict and per-criterion results

---

## T06 — Claude acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T05
- **title:** Validate F0 and write final acceptance result

**Scope:**
- Read `review.md` produced by T05
- Verify all acceptance criteria in `acceptance.md` are addressed
- Write `final-report.md` with disposition `accepted` or `failed`
- If `failed`: note specific failing criteria and return affected tasks to `pending` in `status.json`
- Update `status.json` feature status to `done` or `failed`

**Done condition:** `final-report.md` written with a clear disposition; `status.json` updated to reflect final feature state
