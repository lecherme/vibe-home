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
| `fix-reports/fix-report-<TICKET_ID>.md` | Codex stdout via `run_fix_codex.sh` | Fix patch summary, verification results, open issues per ticket |
| `fix-reports/fix-report-<TICKET_ID>.log` | stderr via `run_fix_codex.sh` | Diagnostic log (debugging only, not read by orchestration flow) |

### `status.json` structure

```json
{
  "feature": "F1-auth",
  "status": "in_progress",
  "current_stage": "T02_done",
  "current_owner": null,
  "next_step": "Start T03 — Claude: acceptance",
  "last_review_failure": null,
  "tasks": [
    {
      "id": "T01",
      "title": "Codex: implement JWT middleware",
      "owner": "codex",
      "type": "build",
      "depends_on": [],
      "status": "done",
      "retry_count": 0,
      "artifact": "codex-build-T01.md"
    }
  ],
  "activity_log": [
    { "timestamp": "2026-04-23T10:00:00Z", "event": "T01 started — Codex: implement JWT middleware", "by": "claude" }
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

The task sequence for a feature is defined by its `tasks.md`. Claude reads `tasks.md` to determine what tasks exist, who owns them, and what their dependencies are. The sequence below is a common example for full-stack features — it is not a mandatory template.

**Common example (full-stack feature):**

1. **Spec** — Claude writes `spec.md`, `tasks.md`, `acceptance.md`, initializes `status.json`
2. **Skeleton** — Codex scaffolds folder structure, empty files, type stubs; wrapper captures `codex-build-<TASK_ID>.md`
3. **Backend** — Codex implements FastAPI router + service + schema; wrapper captures `codex-build-<TASK_ID>.md`
4. **UI** — Gemini scaffolds page + components using published API types; wrapper captures `gemini-build-<TASK_ID>.md`
5. **Review** — Codex reviews all artifacts against `acceptance.md`; writes `review.md`
6. **Acceptance** — Claude reads `review.md`, writes `final-report.md`, updates `status.json`

Features with narrower scope (e.g. backend-only parser changes) may have fewer tasks — for example T01 build, T02 review, T03 acceptance. The number and type of tasks varies; always follow `tasks.md` for the feature being worked on.

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

---

## Running the Eval Suite (F16)

The runtime backend container image does **not** include `backend/tests/`. Do not
attempt to find or run tests inside the running `backend` container.

Standard command (always use this):

```bash
bash tools/run_eval.sh
```

This mounts `backend/tests/` into a one-off container at `/app/tests` and runs
`pytest /app/tests/test_eval.py -q`. Any extra pytest flags can be appended.

Do **not** use:
- `docker compose exec backend python3 -m pytest ...` — tests are not in the image
- `docker cp` to push test files into the live container
- Host-level `python3 tests/test_eval.py` — backend deps are not installed on host

---

## Fix Ticket Schema

Fix tickets are the execution units of the review-fix loop. Each ticket lives under
an affected task's `fix.tickets[]` array in `status.json` and is executed by
`tools/run_fix_codex.sh`.

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique ID within the feature. Format: `fix-<criterion>-<short-desc>` |
| `required_by` | Yes | Review task ID that exposed this issue (e.g. `"T05"`) |
| `affected_task` | Yes | Original build task this fix targets (e.g. `"T02"`) |
| `affected_task_title` | Yes | Human-readable title of the affected task |
| `criterion` | Yes | The review failure label as it appears in `review.md` (e.g. `"A2"`, `"J8"`, `"SEC-01"`). This is whatever label the review artifact assigned — not a fixed naming scheme. Do not invent new labels; copy verbatim from the review. |
| `status` | Yes | `pending` \| `in_progress` \| `done` \| `failed` |
| `files` | Yes | Strict list of files Codex may modify. Any modification to an unlisted file is a contract violation. |
| `description` | Yes | One sentence: what to delete or replace, and why |
| `verification` | Yes | Shell command string. exit 0 = fix confirmed. Must be minimal, stable, and reproducible. Do not encode multi-step logic into a single line — write a small script instead if the check requires more than one operation. |
| `pre_condition` | No | Ticket ID that must reach `done` before this ticket may start |

### Task-level fix sub-object (status.json)

```json
"fix": {
  "status": "in_progress",
  "tickets": [
    {
      "id": "fix-A2-supabase",
      "required_by": "T05",
      "affected_task": "T02",
      "affected_task_title": "Backend persistence rewrite",
      "criterion": "A2",
      "status": "pending",
      "files": ["backend/app/core/supabase.py"],
      "description": "Remove FakeSupabaseClient fallback; raise on missing Supabase config instead of silently falling back to in-memory storage",
      "verification": "python3 -c \"import sys; sys.exit(0 if 'FakeSupabaseClient' not in open('backend/app/core/supabase.py').read() else 1)\"",
      "pre_condition": null
    }
  ]
}
```

`fix.status`: `in_progress` when any ticket is pending or in_progress; `done` when all tickets are done.

### Review task fields added on fix_loop entry (status.json)

```json
{
  "id": "T05",
  "status": "failed_review",
  "failed_review": {
    "verdict": "FAIL",
    "artifact": "review.md",
    "failed_criteria": ["A2", "A5"],
    "timestamp": "2026-05-03T15:09:55Z"
  },
  "blocked_by_fixes": ["fix-A2-supabase", "fix-A5-test-admin"]
}
```

`blocked_by_fixes` lists only code-fix ticket IDs. Deployment or environment
verification items (e.g. Docker end-to-end) are handled by task reruns, not fix tickets.

---

## Patch-Only Fix Discipline

Fix tickets enforce a stricter variant of the general Minimal Diff discipline.

1. **Scope is the only truth.** Codex may only modify files listed in `ticket.files`. Any change to an unlisted file is a contract violation; Codex must record it as a blocker in the fix report and stop.
2. **No net additions.** A fix ticket removes or replaces problem symbols. It does not add new features, refactor unrelated code, or extend interfaces.
3. **Verification is mandatory.** `ticket.verification` must be run immediately after the patch. A ticket is not `done` until verification exits 0. If verification fails, ticket status is `failed`; do not mark done.
4. **One criterion per ticket.** Each ticket targets exactly one review failure label. If two criteria require changes to the same file, create two tickets — one per criterion.
5. **File budget.** A single ticket must not modify more than three files. If the fix requires more, split into multiple tickets using `pre_condition` chaining.

---

## Fix Report Format

Every fix ticket execution via `tools/run_fix_codex.sh` must produce a fix report.
Claude reads the fix report to determine whether to mark the ticket `done` or `failed`.

### Path and naming

```
.ai/features/<feature>/fix-reports/fix-report-<TICKET_ID>.md   ← structured report (stdout)
.ai/features/<feature>/fix-reports/fix-report-<TICKET_ID>.log  ← diagnostic log (stderr)
```

### Minimum content structure

```markdown
# Fix Report: <ticket-id>

## Ticket Info
- **Review Task:** <required_by>
- **Affected Task:** <affected_task> — <affected_task_title>
- **Criterion:** <criterion>
- **Files Declared:** <files list>

## Files Changed
- <list of files actually modified>

## Patch Summary
<One to three sentences: what was deleted or replaced.>

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `<verification command>` | `<actual output or exit code>` | PASS / FAIL |

## Open Issues
<None, or list remaining concerns for Claude to evaluate.>
```

### Retroactive claiming without fix report (migration special case — one-time only)

Fix tickets may be marked `done` without a fix report **only** when the code
changes were applied before the fix loop framework existed (i.e., during an
earlier direct-fixup before this schema was defined). This exception applies
**once, to the initial migration** of a feature into fix loop. The `activity_log`
entry for that migration must explicitly note which tickets were retroactively
claimed and that no fix report was generated. All subsequent ticket executions
via `run_fix_codex.sh` must produce a fix report. No further exceptions.
