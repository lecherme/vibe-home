# Conventions

## Folder Structure

```
vibe_home/
├── .ai/                        # project planning docs (not shipped)
│   └── features/               # one workspace per feature
│       └── <feature>/          # e.g. f0-foundation/, f1-auth/
│
├── frontend/                   # Next.js app
│   ├── app/                    # App Router pages and layouts
│   │   ├── (auth)/             # auth route group
│   │   ├── (main)/             # main app route group
│   │   └── admin/              # admin-only pages
│   ├── components/
│   │   ├── ui/                 # shadcn primitives (do not edit)
│   │   └── features/           # feature-scoped components
│   │       └── [feature]/      # e.g. properties/, favorites/, search/
│   ├── lib/
│   │   ├── api/                # typed fetch wrappers for FastAPI endpoints
│   │   └── auth/               # Supabase auth helpers
│   └── types/                  # shared TypeScript types (mirrored from backend schemas)
│
├── backend/                    # FastAPI app
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── [feature]/  # routers per feature
│   │   ├── core/               # config, security, dependencies
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # business logic layer
│   │   │   └── search/         # search module (internal until extracted)
│   │   └── main.py
│   └── tests/
│
└── search-service/             # extracted search service (created in F3 or later)
    ├── app/
    │   ├── api/
    │   ├── core/
    │   └── main.py
    └── tests/
```

---

## Feature Workspace Conventions

Every feature gets a workspace at `.ai/features/<feature>/`.

### Required files (written before implementation begins)

| File | Owner | Purpose |
|------|-------|---------|
| `spec.md` | Claude | Goal, non-goals, acceptance criteria, dependencies |
| `tasks.md` | Claude | Ordered task list with owner and dependency per task |
| `owner.md` | Claude | Which owner is active and what they are doing |
| `acceptance.md` | Claude | Checklist of criteria Codex review must verify |
| `status.json` | Claude only | Canonical task statuses + activity log |

### Generated artifacts (written during/after implementation)

| File | Owner | Purpose |
|------|-------|---------|
| `codex-build-report.md` | Codex | Files changed, tests written, API types published, open issues |
| `gemini-build-report.md` | Gemini | Components created, pages scaffolded, open issues |
| `review.md` | Codex | Review findings: pass/fail per acceptance criterion, required fixes |
| `final-report.md` | Claude | Acceptance decision, criteria met/failed, disposition |

### `status.json` structure

```json
{
  "feature": "f1-auth",
  "status": "in_progress",
  "tasks": [
    {
      "id": "t1",
      "name": "JWT middleware",
      "owner": "codex",
      "status": "done",
      "artifact": "codex-build-report.md"
    }
  ],
  "activity_log": [
    { "timestamp": "2026-04-23T10:00:00Z", "event": "task t1 started", "by": "claude" }
  ]
}
```

Only Claude writes to `status.json`. No other owner may modify it.

---

## Naming Conventions

### Frontend
- Files: `kebab-case` (`property-card.tsx`, `use-favorites.ts`)
- Components: `PascalCase` exports (`PropertyCard`, `SearchBar`)
- Hooks: `use` prefix (`useFavorites`, `usePropertyList`)
- API wrappers: noun + verb (`propertiesApi.getById`, `favoritesApi.add`)
- Types: `PascalCase`, no `I` prefix (`Property`, `SearchFilters`)

### Backend
- Files: `snake_case` (`property_router.py`, `property_service.py`)
- Classes: `PascalCase` (`PropertyService`, `PropertyCreate`)
- Functions/variables: `snake_case`
- Pydantic schemas: suffix by intent (`PropertyCreate`, `PropertyRead`, `PropertyUpdate`)
- Router prefix: `/api/v1/[feature]`

---

## Frontend / Backend Layering

```
Page (app/)
  └── calls → lib/api/[feature].ts      ← typed fetch wrapper
                  └── calls → FastAPI endpoint
                                └── calls → service layer
                                              └── calls → Supabase / search module
```

Rules:
- Pages and components never import from `services/` or call Supabase directly
- `lib/api/` is the only place that constructs fetch calls
- Components receive data as props or from hooks — no inline fetching in JSX
- All API response types must be defined in `frontend/types/` and kept in sync with backend Pydantic schemas

---

## Config / Env Conventions

- All env vars are prefixed by service: `NEXT_PUBLIC_*` (frontend public), `API_*` (backend), `SEARCH_*` (search service)
- `.env.example` is committed; `.env.local` / `.env` are gitignored
- No hardcoded URLs, keys, or secrets anywhere in source
- Feature flags: `NEXT_PUBLIC_FEATURE_AI_SEARCH=false` — checked in one place only

Required env vars per service are documented in each service's `README.md`.

---

## Feature Workflow Conventions

Every feature follows this sequence of sequential tasks:

1. **Spec** — Claude writes `spec.md`, `tasks.md`, `acceptance.md`, initializes `status.json`
2. **Skeleton** — Codex scaffolds folder structure, empty files, type stubs; writes `codex-build-report.md`
3. **Backend** — Codex implements FastAPI router + service + schema; writes `codex-build-report.md`
4. **UI** — Gemini scaffolds page + components using published API types; writes `gemini-build-report.md`
5. **Review** — Codex reviews all artifacts against `acceptance.md`; writes `review.md`
6. **Acceptance** — Claude reads `review.md`, writes `final-report.md`, updates `status.json`

No task begins until its declared dependency task has a complete output artifact.
No feature is done until Claude writes `final-report.md` with a passing disposition.
