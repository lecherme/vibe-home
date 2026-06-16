# vibe_home

A full-stack Hong Kong property listing platform — and a **production demonstration of multi-agent orchestration layer**. Every feature in this project is designed, implemented, reviewed, and accepted by a structured pipeline of AI agents coordinated through a file-based state machine.

The codebase itself is the output. The orchestration system is the methodology.

---

## Multi-Agent Orchestration

### Philosophy

This project treats AI agents as structured team members with declared ownership, bounded file scopes, and enforced review gates. No agent can unilaterally modify another agent's artifacts. No feature advances without passing acceptance criteria. The entire delivery process is auditable from git history and the `.ai/` directory.

### The `.ai/` Directory

Everything that governs how features are built lives here:

```
.ai/
├── orchestration.md      # Full system spec: lifecycle, state machine, roles, escalation rules
├── conventions.md        # Code style, naming, file layout, commit format
├── architecture.md       # System architecture decisions and constraints
├── owner-system.md       # Agent ownership model and boundary rules
├── permissions.md        # What each agent can and cannot modify
├── roadmap.md            # Feature pipeline: F0→F∞, sequencing, dependencies
│
└── features/
    └── F{n}-{name}/
        ├── spec.md                          # Feature specification (goals, scope, non-goals)
        ├── tasks.md                         # Task breakdown, per-task file scopes, done conditions
        ├── acceptance.md                    # Acceptance criteria A1..An with verification steps
        ├── status.json                      # State machine — single source of truth
        ├── task_manifest.json               # File-level boundary enforcement (per task)
        ├── owner.md                         # Current task owner declaration
        │
        ├── codex-build-T{n}.md             # Build artifact: what Codex did, files changed
        ├── codex-build-T{n}.log            # Raw Codex execution log
        │
        ├── review.md                        # Latest Codex review (PASS/FAIL + per-criterion notes)
        ├── codex-review.log                 # Raw review execution log
        ├── review.attempt-{timestamp}.md   # Archived failed review attempts
        ├── codex-review.attempt-{ts}.log   # Archived failed review logs
        │
        └── final-report.md                  # Claude acceptance report (ACCEPTED/REJECTED)
```

#### `status.json` — the state machine

Every feature has a `status.json` that tracks the live state of the pipeline:

```jsonc
{
  "feature": "F8-production-hardening",
  "status": "done",               // pending | in_progress | done
  "current_stage": "T06_done",
  "current_owner": null,          // which agent currently owns the task
  "tasks": [
    { "id": "T01", "owner": "codex", "type": "build", "status": "done" },
    { "id": "T05", "owner": "codex", "type": "review", "status": "done", "retry_count": 1 },
    { "id": "T06", "owner": "claude", "type": "acceptance", "status": "done" }
  ],
  "last_review_failure": { ... },  // populated on FAIL, cleared on PASS
  "activity_log": [ ... ]          // append-only audit trail with timestamps and agents
}
```

**Only Claude writes `status.json`.** Codex and Gemini cannot modify it. This is enforced by `status_guard.py`.

### Feature Lifecycle

```
  Claude initializes workspace (spec, tasks, acceptance, status.json, task_manifest.json)
        │
        ▼
  T01..Tn  ──► Codex executes build task within declared file scope
  (build)       │
                ├── artifact: codex-build-T{n}.md + .log
                └── Claude updates status.json
        │
        ▼
  T{review} ──► Codex reviews against acceptance criteria A1..An
  (review)      │
                ├── PASS ──► Claude runs acceptance
                │
                └── FAIL ──► Claude diagnoses failure
                              │
                              ├── direct_fixup
                              │     Claude applies minimal fix directly,
                              │     writes fix notes to status.json,
                              │     triggers review retry
                              │
                              ├── fix_task  (the fix-ticket loop)
                              │     Claude opens a scoped fix task (e.g. T02-fix),
                              │     dispatches to Codex via run_fix_codex.sh,
                              │     fix artifact captured as fix-report-T{n}.md,
                              │     review retries after fix lands
                              │
                              └── reject
                                    Feature rejected back to spec or escalated
        │
        ▼
  T{acceptance} ──► Claude verifies end-to-end, writes final-report.md
                    │
                    ├── ACCEPTED ──► feature done, next_feature.sh advances pipeline
                    └── REJECTED ──► escalate or redesign
```

The **fix-ticket loop** is the core quality mechanism: a review FAIL does not block the pipeline — it opens a tracked fix task with its own scope declaration in `task_manifest.json`, its own Codex run, and its own artifact (`fix-report-T{n}.md`). Retry counts and failure details are preserved in `status.json` under `last_review_failure`. All failed review artifacts are archived with timestamps — the complete failure history is traceable in the feature directory.

### Orchestration Tools

```
tools/
├── run_task.sh          # Dispatch a build task to Codex with scope enforcement
├── run_codex_review.sh  # Run structured review against acceptance.md criteria
├── run_fix_codex.sh     # Dispatch a scoped fix task after a review FAIL (fix-ticket loop)
├── run_codex.sh         # General-purpose Codex execution
├── run_gemini.sh        # Gemini agent execution (alternative reviewer / second opinion)
├── next_feature.sh      # Advance the pipeline to the next feature in roadmap.md
├── new_feature.sh       # Initialize a new feature workspace from template
├── resume.sh            # Resume an in-progress feature after context reset
├── run_eval.sh          # Run AI search eval suite (mounts backend/tests into a fresh container)
├── git_checkpoint.sh    # Commit current state with structured message
└── status_guard.py      # Validates status.json writes — blocks unauthorized agents
```

**`status_guard.py`** is the enforcement layer. Before any `status.json` write is committed, it verifies:
- The writing agent matches the declared owner
- The state transition is valid
- No agent has modified files outside its declared scope in `task_manifest.json`

---

## Product Capabilities

- **Auth & role management** — Supabase Auth (PKCE, ES256 JWT), admin-gated routes
- **Property browsing & favorites** — paginated listings, per-user favorites, image upload to Supabase Storage
- **Structured search** — filter by location, price, bedrooms, area, build year, subway distance
- **Hybrid AI search** — natural-language query → deterministic parser + LLM vocabulary recognition → pgvector semantic retrieval → LLM summary
- **Query parser** — regex-based normalization, Chinese vocabulary support, subjective comparison mapping
- **Relaxation layer** — when strict filters return 0 results, progressively relaxes soft constraints and discloses what changed
- **Intent guard** — classifies queries before pipeline entry; non-property queries exit early with a redirect message
- **Production hardening** — CORS allowlist, rate limiting, structured JSON logging, cascade delete
- **UI** — shadcn/ui component system throughout (forms, search, admin)

Detailed delivery history: [`.ai/features/`](.ai/features/)

---

## Tech Stack

| Layer | Stack |
|---|---|
| Frontend | Next.js 16.2 (App Router), TypeScript 5.6, Tailwind CSS, shadcn/ui |
| Backend | FastAPI 0.116, Python 3.12, PyJWT (ES256/JWKS) |
| Auth | Supabase Auth (PKCE, ES256 JWT) |
| Database | Supabase (PostgreSQL + pgvector) |
| AI | OpenAI (embeddings + LLM filter parsing + summary) |
| Container | Docker Compose (multi-stage builds) |

---

## Running with Docker

### Development (hot reload)

```bash
# First time — build images
docker compose build

# Start with hot reload (docker-compose.override.yml applied automatically)
docker compose up
```

- **Backend**: `./backend/app` is volume-mounted; uvicorn runs with `--reload`
- **Frontend**: `./frontend` is volume-mounted; Next.js runs in dev mode
- Code changes take effect immediately — no rebuild needed unless `requirements.txt` or `package.json` changes

### Production

```bash
docker compose -f docker-compose.yml up --build
```

---

## Environment Variables

### Backend (`backend/.env`)

```env
SUPABASE_URL=https://<ref>.supabase.co
SUPABASE_KEY=<service-role-key>                # backend Supabase client key
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>   # required — used directly by supabase.py for admin operations
SUPABASE_ANON_KEY=<anon-key>                   # reference only
SUPABASE_JWT_SECRET=<jwt-secret>               # optional; JWT verification uses Supabase JWKS (ES256)
ALLOWED_ORIGINS=http://localhost:3000          # required; comma-separated allowed CORS origins
CORS_ALLOWED_ORIGINS=https://yourdomain.com    # optional; takes priority over ALLOWED_ORIGINS in production
RATE_LIMIT_AUTH=5/minute                       # optional; default 5/minute; format: <count>/<second|minute|hour|day>

# AI search
EMBEDDING_API_KEY=<key>                        # API key for embedding provider
EMBEDDING_MODEL=embedding-3                    # embedding model name
EMBEDDING_BASE_URL=https://...                 # embedding provider base URL
LLM_PROVIDER=openai                            # anthropic | openai | openai_compatible
LLM_API_KEY=<key>                              # LLM API key
LLM_MODEL=claude-3-5-haiku-latest             # LLM model name
LLM_BASE_URL=https://...                       # optional; required for openai_compatible provider
```

### Frontend

Local development uses `frontend/.env.local`; Docker Compose reads `frontend/.env`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://<ref>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon-key>
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Local Development (without Docker)

### Backend

```bash
cd backend
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
cp .env.example .env.local
npm install && npm run dev
```

---

## Seed Data

Sample data with 20 Hong Kong properties is available at `backend/seeds/001_seed_properties.sql`. Run it in Supabase Studio's SQL editor to populate the database for local development.

---

## API Reference

| Endpoint | Auth | Description |
|---|---|---|
| `GET /health` | — | Health check |
| `GET /api/v1/auth/me` | Bearer | Current user (rate-limited: 5/min) |
| `GET /api/v1/properties` | Bearer | List properties (paginated) |
| `GET /api/v1/properties/{id}` | Bearer | Property detail |
| `GET /api/v1/properties/search` | Bearer | Structured search with filters |
| `POST /api/v1/search/ai` | Bearer | AI search — natural-language query, returns parsed filters + summary |
| `GET /api/v1/favorites` | Bearer | User favorites |
| `POST /api/v1/favorites/{id}` | Bearer | Add to favorites |
| `DELETE /api/v1/favorites/{id}` | Bearer | Remove from favorites |
| `GET /api/v1/admin/properties` | Bearer (admin) | List all properties (admin) |
| `POST /api/v1/admin/properties` | Bearer (admin) | Create property |
| `PUT /api/v1/admin/properties/{id}` | Bearer (admin) | Update property |
| `DELETE /api/v1/admin/properties/{id}` | Bearer (admin) | Delete + cascade favorites |
| `POST /api/v1/admin/uploads/property-image` | Bearer (admin) | Upload image to Supabase Storage |
| `POST /api/v1/admin/embeddings/sync` | Bearer (admin) | Sync property embeddings for AI search |
