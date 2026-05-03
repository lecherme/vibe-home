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
| `codex-build-<TASK_ID>.md` | Codex stdout via wrapper | Files changed, tests written, API types published, open issues |
| `gemini-build-<TASK_ID>.md` | Gemini stdout via wrapper | Components created, pages scaffolded, open issues |
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
      "artifact": "codex-build-T01.md"
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
2. **Skeleton** — Codex scaffolds folder structure, empty files, type stubs; wrapper captures `codex-build-<TASK_ID>.md`
3. **Backend** — Codex implements FastAPI router + service + schema; wrapper captures `codex-build-<TASK_ID>.md`
4. **UI** — Gemini scaffolds page + components using published API types; wrapper captures `gemini-build-<TASK_ID>.md`
5. **Review** — Codex reviews all artifacts against `acceptance.md`; writes `review.md`
6. **Acceptance** — Claude reads `review.md`, writes `final-report.md`, updates `status.json`

No task begins until its declared dependency task has a complete output artifact.
No feature is done until Claude writes `final-report.md` with a passing disposition.

---

## Worker Modification Discipline

Workers apply only the minimum change needed to satisfy the task's **Done condition**. This discipline takes precedence over any judgment call to improve, clean up, or extend code beyond task scope.

### 1. Scope Gate (highest priority)

- A worker may only modify, create, or delete files explicitly listed in the current task's **`Scope:`** block in `tasks.md`.
- If a required change touches a file not on that list, the worker must:
  1. Write the blocker in `## Open Issues` (exact filename + reason)
  2. Stop the task immediately
  3. Do NOT modify the out-of-scope file
  4. Wait for Claude to update the `tasks.md` Scope before retrying

Do not expand scope unilaterally under any circumstances.

**Exception — Registration-only additions:** If the out-of-scope file is a barrel/index export file, a route registry file, or an i18n translation file, AND the entire change is (a) purely additive — no deletions, no logic changes — and (b) ≤ 3 lines total, you MAY apply the change without stopping. You MUST record it in `## Files Changed` with the tag `(registration-only exemption)`. All other out-of-scope modifications still require immediate stop + blocker.

### 2. Minimal Diff

- Patch existing files in-place. Do not rewrite whole files.
- A full-file rewrite is permitted **only** when a targeted patch is structurally impossible — e.g. the file is corrupted or contains irreconcilable duplication from a previous failed attempt.
- Any full-file rewrite requires an explicit justification written in `## Open Issues`.
- Do not rename identifiers, reorder imports, adjust formatting, or reorganize code outside the lines required to complete the task.
- Do not add new directories, rename files, or change module organization unless the task explicitly requires it.
- Do not refactor, clean up, or improve code that is outside the task's Done condition.

### 3. Idempotent Implementation

- Inspect existing target files before writing.
- If a file is missing, create it.
- If a file exists and is incomplete, patch it minimally (§2 above).
- Do not append duplicate functions, exports, routes, schemas, tests, or imports.
- Do not create alternative filenames such as `*_v2`, `*_new`, `*_fixed`.
- Keep file paths stable and task-scoped.
- Re-running this task must not introduce duplicate code or artifacts.
- When adding to a registry/router/index file, check whether the entry already exists before adding.
- When modifying existing code, preserve unrelated behavior.

### 4. Reporting

- Every file modified, created, or deleted must appear in the build report's `## Files Changed` section.
- Files inspected but not changed must NOT appear in `## Files Changed`.

---

## Dev Requirements

- jq (for git checkpoint script)
