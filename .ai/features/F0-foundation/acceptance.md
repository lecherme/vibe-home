# F0 — Acceptance Criteria

T05 (Codex review) verifies every criterion below and writes `review.md`.
T06 (Claude acceptance) reads `review.md` and writes `final-report.md` with the final disposition.

---

## Backend (T01)

| # | Criterion | Check |
|---|-----------|-------|
| B1 | `backend/` folder structure matches `.ai/conventions.md` | Verify folders: `api/v1/`, `core/`, `models/`, `schemas/`, `services/` |
| B2 | `GET /health` returns 200 with `{ "status": "ok" }` | Run `curl http://localhost:8000/health` |
| B3 | Supabase config fields declared in `core/config.py` and loaded from env; `.env.example` contains placeholder values only — no live connection required | Check `config.py` reads `SUPABASE_URL` and `SUPABASE_KEY` from env; verify no hardcoded credentials; verify `.env.example` uses placeholder strings |
| B4 | `.env.example` documents all required backend env vars | Check file contains: `SUPABASE_URL`, `SUPABASE_KEY`, `ALLOWED_ORIGINS` |
| B5 | `uvicorn app.main:app` starts without errors | Run dev server; no import errors or crashes |
| B6 | No business logic beyond health endpoint | Verify no other endpoints or service functions exist |

## Frontend (T02)

| # | Criterion | Check |
|---|-----------|-------|
| F1 | `frontend/` folder structure matches `.ai/conventions.md` | Verify folders: `app/`, `components/ui/`, `components/features/`, `lib/api/`, `lib/auth/`, `types/` |
| F2 | Next.js App Router initialized | Check `app/layout.tsx` exists |
| F3 | Tailwind CSS configured | Check `tailwind.config.ts` exists; no config errors |
| F4 | shadcn/ui initialized | Check `components.json` exists; `components/ui/` is empty but ready |
| F5 | `.env.example` documents all required frontend env vars | Check file contains: `NEXT_PUBLIC_API_URL` |
| F6 | `next dev` starts without errors | Run dev server; no TypeScript or build errors |

## Health Page (T03)

| # | Criterion | Check |
|---|-----------|-------|
| H1 | `frontend/app/page.tsx` exists and renders | Visit `http://localhost:3000` |
| H2 | Page fetches `GET ${NEXT_PUBLIC_API_URL}/health` on load | Check network tab or code |
| H3 | Page displays backend response status | Verify "ok" or error message is shown |
| H4 | Page uses env var for API URL; falls back to `http://localhost:8000` | Check code uses `process.env.NEXT_PUBLIC_API_URL` |
| H5 | No business logic in page — only fetch and display | Verify no data transformation, validation, or auth checks |
| H6 | Clear error state when backend is unreachable | Stop backend; verify page shows error, not crash |

## Documentation (T04)

| # | Criterion | Check |
|---|-----------|-------|
| D1 | `README.md` exists at repo root | Check file exists |
| D2 | README includes project overview | Verify one-paragraph description |
| D3 | README lists prerequisites | Check Node version, Python version documented |
| D4 | README has backend setup steps | Verify: copy `.env.example`, install deps, run server |
| D5 | README has frontend setup steps | Verify: copy `.env.example`, install deps, run server |
| D6 | README has verification steps | Verify: visit health page, check `/health` endpoint |

## Review and Acceptance (T05 + T06)
If T05 verdict is FAIL, Claude must update the failed task(s) in status.json back to pending before retry.
**T05 — Codex review** runs `tools/run_codex_review.sh` and writes `review.md` containing:
- A per-criterion PASS/FAIL table covering B1–B6, F1–F6, H1–H6, D1–D6
- A list of issues found (BLOCKER / WARNING / MINOR)
- A list of required fixes for any blockers
- An overall verdict: PASS or FAIL

**T06 — Claude acceptance** reads `review.md` and writes `final-report.md` containing:
- Final disposition: `accepted` or `failed`
- If `failed`: the specific criteria that failed and which tasks must be retried
- Claude then updates `status.json` feature status to `done` or `failed`

`final-report.md` is written only by Claude in T06. It is never written for intermediate blocked or failed task states.

---

## Rejection Conditions

Codex review (T05) must mark the verdict as **FAIL** if any of these are true:

- Any criterion above is not met
- Hardcoded secrets or URLs in source code
- Business logic in frontend components (T03)
- Folder structure does not match `.ai/conventions.md`
- Dev servers do not start without errors
- `status.json` was modified by Codex or Gemini (only Claude may write to it)
