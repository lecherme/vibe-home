# Orchestration

Claude is the only orchestrator. Codex and Gemini are execution workers.
Execution is serial. Every task has exactly one owner.

---

## Execution Flow

### Step 1 — Claude reads the feature workspace

Before invoking any worker, Claude reads:
- `.ai/features/<feature>/spec.md` — what the feature is and what it must do
- `.ai/features/<feature>/tasks.md` — ordered task list with owner and dependencies
- `.ai/features/<feature>/owner.md` — static ownership map: which tasks belong to which owner, and per-owner constraints
- `.ai/features/<feature>/status.json` — current runtime state: task statuses, active task, and activity log

`owner.md` is a static reference document written once by Claude before implementation begins. It does not change as tasks progress. The current runtime state — which task is active, what has completed — comes exclusively from `status.json`.

Claude determines the next task by finding the first task whose:
- status is `pending`
- all declared dependency tasks have status `done`

If no such task exists and some tasks are still `pending`, the feature is blocked. Claude updates `status.json` to mark the feature status as `blocked`, appends a blocker entry to `activity_log` with the reason, and stops. `final-report.md` is not written for intermediate blocked states — it is reserved for final acceptance outcomes only.

### Step 2 — Claude invokes the correct worker

Based on the task's `owner` field:

| Owner | Command |
|-------|---------|
| `codex` | `tools/run_codex.sh .ai/features/<feature> <TASK_ID>` |
| `gemini` | `tools/run_gemini.sh .ai/features/<feature> <TASK_ID>` |

Claude passes the feature directory path. The script reads all required files and constructs the prompt internally.

### Step 3 — Worker executes; wrapper captures output

The worker outputs its report to stdout only. The wrapper script captures stdout into the feature-scoped artifact and stderr into the log file. Workers must NOT create report files themselves. Any attempt to write report files directly is a contract violation.

| Worker | Report artifact (wrapper captures stdout) | Diagnostic log (stderr) |
|--------|-------------------------------------------|------------------------|
| Codex | `<feature>/codex-build-<TASK_ID>.md` | `<feature>/codex-build-<TASK_ID>.log` |
| Gemini | `<feature>/gemini-build-<TASK_ID>.md` | `<feature>/gemini-build-<TASK_ID>.log` |

`codex-build-<TASK_ID>.md` and `gemini-build-<TASK_ID>.md` are structured report artifacts written by the wrapper from the worker's stdout. They are the authoritative record of what was built and are read by Claude and Codex review.

`codex-build-<TASK_ID>.log` and `gemini-build-<TASK_ID>.log` are diagnostic logs from stderr. They are for debugging only and are not read as part of the orchestration flow.

### Step 4 — Claude reads the artifact and updates status.json

Claude reads the output artifact and:
- Updates the completed task's status to `done` in `status.json`
- Appends an entry to `activity_log` with timestamp, event, and owner
- Determines the next task (back to Step 1)

Claude is the only writer of `status.json`.

### Step 5 — Claude invokes Codex review

After all implementation tasks are done, Claude invokes:

```
tools/run_codex_review.sh .ai/features/<feature> <TASK_ID>
```

Codex reads `acceptance.md` and all implementation artifacts, then writes `review.md`.

### Step 6 — Claude performs final acceptance

Claude reads `review.md` and makes the acceptance decision:

- **Pass** — Claude writes `final-report.md` with disposition `accepted`, updates `status.json` feature status to `done`
- **Fail** — Claude writes `final-report.md` with disposition `failed` and specific failure notes, updates the failed task(s) back to `pending`, returns to Step 1

There is no self-acceptance. Claude's `final-report.md` is required for every feature.

---

## Task Execution Rules

- One task runs at a time. No parallel execution.
- A task may not start until all tasks in its `depends_on` list have status `done`.
- If a task fails (worker exits non-zero or artifact is missing), Claude marks it `failed` in `status.json` and stops the feature run.
- A task marked `blocked` requires Claude to resolve the blocker before re-queuing.

## Dependency Handling

Dependencies are declared per task in `tasks.md` as a list of task IDs.
Claude evaluates dependencies at runtime by reading `status.json`, not by static ordering alone.
If a dependency is in a different feature, that feature must be fully `done` before this feature begins.

## Artifact Lifecycle

| Artifact | Created by | Read by | Immutable after? |
|----------|-----------|---------|-----------------|
| `spec.md` | Claude | All | Yes — changes require a new spec version |
| `tasks.md` | Claude | All | No — Claude may add tasks during a feature run |
| `owner.md` | Claude | Workers | Yes — static ownership map written once before implementation |
| `acceptance.md` | Claude | Codex (review) | Yes — changes require re-review |
| `status.json` | Claude | All | No — updated after every task |
| `codex-build-<TASK_ID>.md` | Codex | Claude, Codex (review) | Yes — rewritten only if task is retried |
| `gemini-build-<TASK_ID>.md` | Gemini | Claude, Codex (review) | Yes — rewritten only if task is retried |
| `review.md` | Codex | Claude | Yes — rewritten only if review is retried |
| `final-report.md` | Claude | Human | Yes |

## State Update Rules

- `status.json` is updated by Claude after every task completion, failure, or block.
- Feature-level `status` in `status.json` transitions: `pending` → `in_progress` → `done` | `failed` | `blocked`
- Task-level `status` transitions: `pending` → `in_progress` → `done` | `failed` | `blocked`
- A feature is `done` only when `final-report.md` exists with disposition `accepted`.
- `final-report.md` is written only for final acceptance outcomes (accepted or failed after review), never for intermediate blocked states.

### status.json edit discipline
- Only modify the exact fields required — never rewrite adjacent objects
- Never remove or reflow array structure
- `activity_log` is append-only: never delete or modify existing entries, always add a new entry at the end

### Verification output discipline
- Each table or section must appear exactly once
- No repeated blocks
- Stop after full coverage is achieved

---
## CI Responsibilities

CI (or human local environment) is responsible for runtime validation.

### Responsibilities
- Install dependencies (backend + frontend)
- Start backend service (uvicorn)
- Start frontend (Next.js dev server)
- Execute runtime verification checklist
- Validate success and failure scenarios

### Notes
- Runtime validation is NOT required inside Codex/Gemini sandbox
- Sandbox reviews may mark runtime criteria as DEFERRED
- CI is the source of truth for runtime correctness

### Trigger Conditions
CI should be triggered:
- At feature completion (e.g. F0, F3, F7)
- Before final acceptance
- When integration-heavy features are introduced

---
## Git Responsibilities

Claude may perform git operations under controlled conditions.

### Allowed
- git add
- git commit

### Conditional
- git push is allowed ONLY IF:
  - final-report.md exists
  - disposition is accepted or accepted_with_caveat

### Forbidden
- git reset --hard
- git rebase
- git clean -fd

### Notes
- Workers (Codex, Gemini) MUST NOT run git commands
- Claude is the only agent allowed to modify repository history
---

## Feature Workspace Layout

```
.ai/features/<feature>/
├── spec.md                   # Claude — feature definition
├── tasks.md                  # Claude — task list with owners and deps
├── owner.md                  # Claude — static ownership map and per-owner constraints
├── acceptance.md             # Claude — review checklist
├── status.json               # Claude only — runtime state: task statuses + activity log
├── codex-build-<TASK_ID>.md     # Codex — structured report artifact (stdout)
├── codex-build-<TASK_ID>.log           # Codex — diagnostic log (stderr)
├── gemini-build-<TASK_ID>.md    # Gemini — structured report artifact (stdout)
├── gemini-build-<TASK_ID>.log          # Gemini — diagnostic log (stderr)
├── review.md                 # Codex — review findings (stdout)
├── codex-review.log          # Codex — diagnostic log (stderr)
└── final-report.md           # Claude — final acceptance decision only
```

There are no global report files at the repo root. All artifacts are feature-scoped.
