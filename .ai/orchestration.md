# Orchestration

Claude is the only orchestrator. Codex and Gemini are execution workers.
Execution is serial. Every task has exactly one owner.

### Worker invocation rule

`tools/run_task.sh` is the **only** sanctioned entry point for Codex build and review tasks. It provides: preflight checks, `status.json` transitions, artifact capture, scope validation, and git checkpoint.

**Required env vars (this host):** always prefix with `CODEX_MODEL=gpt-5.4 CODEX_BYPASS_SANDBOX=1`. The local bwrap/userns sandbox causes false failures; bypass is mandatory. Standard invocation:

```
CODEX_MODEL=gpt-5.4 CODEX_BYPASS_SANDBOX=1 bash tools/run_task.sh <feature> <task>
```

Agent mode (spawning a general-purpose agent to call Codex directly) is **not** a substitute for `run_task.sh`. Agent mode is permitted only for:
- Read-only exploration or debug probes that do not modify files
- Post-hoc rescue when a run was interrupted after code was written but before an artifact was produced (see Step 3c)

Never use Agent mode as the primary execution path for any worker task that should run through `tools/run_task.sh`, especially Codex build and review tasks.

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

### Step 2 — Claude invokes the task runner

For executable worker tasks, Claude invokes the Claude-owned task runner:

```
tools/run_task.sh .ai/features/<feature> <TASK_ID>
```

`run_task.sh` performs preflight checks, transitions `status.json` to
`in_progress`, invokes the correct worker wrapper, validates the output artifact,
then transitions the task to `done` or `failed`.

Based on the task's `owner` and `type` fields, `run_task.sh` delegates to:

| Owner | Command |
|-------|---------|
| `codex` | `tools/run_codex.sh .ai/features/<feature> <TASK_ID>` |
| `gemini` | `tools/run_gemini.sh .ai/features/<feature> <TASK_ID>` |
| `codex` + `type=review` | `tools/run_codex_review.sh .ai/features/<feature> <TASK_ID>` |

Claude-owned acceptance tasks are not executable through `run_task.sh`. Claude
performs acceptance directly by reading `review.md`, writing `final-report.md`,
and updating `status.json`.

Claude passes the feature directory path. The worker wrapper reads all required files and constructs the prompt internally.

### Step 3 — Worker executes; wrapper captures output

The worker outputs its report to stdout only. The wrapper script captures stdout into the feature-scoped artifact and stderr into the log file. Workers must NOT create report files themselves. Any attempt to write report files directly is a contract violation.

| Worker | Report artifact (wrapper captures stdout) | Diagnostic log (stderr) |
|--------|-------------------------------------------|------------------------|
| Codex | `<feature>/codex-build-<TASK_ID>.md` | `<feature>/codex-build-<TASK_ID>.log` |
| Gemini | `<feature>/gemini-build-<TASK_ID>.md` | `<feature>/gemini-build-<TASK_ID>.log` |

`codex-build-<TASK_ID>.md` and `gemini-build-<TASK_ID>.md` are structured report artifacts written by the wrapper from the worker's stdout. They are the authoritative record of what was built and are read by Claude and Codex review.

`codex-build-<TASK_ID>.log` and `gemini-build-<TASK_ID>.log` are diagnostic logs from stderr. They are for debugging only and are not read as part of the orchestration flow.

### Step 3b — False failure handling (needs_verification)

If `run_task.sh` exits non-zero and the task status is `needs_verification`
(not `failed`), the wrapper detected a possible false failure: the worker exited
non-zero but the artifact exists and passed `validate-artifact`. This is NOT a
confirmation that implementation succeeded — it means the artifact structure is
intact, not that the code is correct. Claude must make the final disposition.

**When this applies:** non-`review` tasks only. Review tasks that exit non-zero
always go directly to `failed` and never enter `needs_verification`.

**Claude's verification steps:**

1. Read the artifact (`codex-build-<TASK_ID>.md` or `gemini-build-<TASK_ID>.md`)
2. Read every file listed in the artifact's `## Files Changed` section
3. Run `python3 tools/status_guard.py validate-artifact <feature> <task_id>` to
   confirm the artifact still passes structural checks
4. For Gemini tasks, inspect the `.log` to characterise the exit cause: retry
   attempts, provider connection errors, and telemetry failures are noise and do
   not indicate implementation failure; errors in file writes, TypeScript
   compilation failures, or missing output files indicate real failure.

**Disposition:**

- Files exist, look correct, and no blocking open issues →
  ```
  python3 tools/status_guard.py verify-pass <feature> <task_id>
  ```
- Any file is missing, wrong, or open issues indicate incomplete work →
  ```
  python3 tools/status_guard.py verify-fail <feature> <task_id> "<reason>"
  ```

Both commands write an explicit `activity_log` entry. `verify-pass` records that
this was a wrapper false failure corrected by Claude. `verify-fail` records that
Claude inspection confirmed a real failure.

`pending_verification` in `status.json` is a helper index (task_id, artifact,
worker exit code, timestamp). It is cleared automatically by both commands.
The canonical state is `task.status = needs_verification` — never rely on
`pending_verification` as a second source of truth.

Claude must not proceed to the next task until a `verify-pass` or `verify-fail`
disposition has been written.

### Step 3c — Manual / Agent implementation rescue

This path applies when code was written via Agent mode or a direct Claude edit — outside of `run_task.sh` — and no artifact was produced.

**When this applies:** the task status is still `pending` or `in_progress`, the implementation files exist and appear correct, but the wrapper was never invoked so no build artifact exists.

**Claude's steps:**

1. Read every modified file and verify the implementation is correct
2. Write the build artifact manually to the standard path with all required sections (`## Task Completed`, `## Files Changed`, `## Summary`, `## Verification`)
3. Run `python3 tools/status_guard.py needs-verification <feature> <task_id>` — do NOT call `done` directly
4. Inspect the artifact and confirm correctness, then call `verify-pass` or `verify-fail` per Step 3b rules

This path does not bypass the artifact requirement or the `needs_verification` gate. It only formalises that Claude, not the wrapper, is responsible for producing the artifact when the standard invocation path was not used.

### Step 4 — Claude validates the artifact and updates status.json

Claude, either directly or through the Claude-owned `run_task.sh` helper, reads
the output artifact and:
- Updates the completed task's status to `done` in `status.json`
- Appends an entry to `activity_log` with timestamp, event, and owner
- Determines the next task (back to Step 1)

For backend, scaffold, and infra tasks (owner=`codex`), Claude must also inspect
the diagnostic log (`codex-build-<TASK_ID>.log`) to confirm that tests were
actually executed and passed. Artifact structural validity does not confirm test
execution — if the log shows no test run or shows a net failure count, Claude
must investigate before treating the task as complete.

For Gemini UI tasks (owner=`gemini`), Claude must confirm that
`gemini-build-<TASK_ID>.md` contains a `## Verification` section, and inspect
the corresponding `.log` to determine whether reported errors represent real
failures or retry/provider noise. Only errors in file creation, TypeScript
compilation, or missing output indicate real failure.

Claude is the only owner of `status.json`. Codex and Gemini workers must never
modify it.

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

**`final-report.md` disposition format (mandatory):**

The disposition line must appear as the first `##`-level heading in the file, on a single line:

```
## Disposition: ACCEPTED
```
or

```
## Disposition: FAILED
```

Multi-line formats are forbidden. The following examples are invalid:

```
## Disposition
ACCEPTED
```
```
## Disposition
accepted
```

Only `ACCEPTED` and `FAILED` are valid values (uppercase). Any other casing or layout is a contract violation.

### Review failure routing

If `review.md` has verdict `FAIL`, Claude must NOT proceed to T06 acceptance.

Claude first classifies the fix path:

- `task_retry`
  - The failed criterion means a worker-owned task was not actually completed.
  - Claude returns the responsible task to `pending`, records retry metadata in
    `status.json`, and reruns the worker task.
- `direct_fixup`
  - The issue is a narrow post-review fix that does not require redoing the
    original worker task.
  - Claude applies the minimum code fix directly, leaves implementation tasks
    `done`, and reruns only the affected review task.
- `review_rerun`
  - Upstream code changed after a direct fixup or manual correction.
  - Claude reruns the review task without replaying the implementation chain.
- `fix_loop`
  - The review exposed multiple well-scoped code removal or replacement issues
    that do not require redoing the original task, but are too numerous for
    Claude to apply inline.
  - Claude leaves the original task(s) `done`. The review task status moves to
    `failed_review`. Fix tickets are created under the affected task(s) in
    `status.json` (see fix ticket schema in `conventions.md`).
  - Codex executes each fix ticket sequentially via `tools/run_fix_codex.sh`.
    Each execution must produce a fix report before Claude proceeds.
  - Claude reads each fix report, updates ticket status and task `fix.status`
    in `status.json`, and resolves `blocked_by_fixes` entries as tickets
    complete. When `blocked_by_fixes` is empty, Claude reruns the review task.
  - `fix_loop` does NOT increment `retry_count` on the original task.

Only when an upstream change materially invalidates downstream implementation
should Claude return downstream implementation tasks to `pending`.

### Failure classification — how Claude chooses the fix path

Before choosing a fix path, Claude classifies every failed criterion:

| failure_type | examples | fix_path |
|---|---|---|
| `wrong_value` | wrong status code, wrong sort order | `direct_fixup` |
| `missing_tests` | edge case not covered | `direct_fixup` |
| `boundary_violation` | fetch() in component, Supabase import outside lib | `task_retry` (violating task only) |
| `type_error` | returns `any` instead of typed interface | `task_retry` (owning task only) |
| `wrong_abstraction` | business logic in page instead of lib/api/ | `task_retry` (owning task only) |
| `logic_error` | pagination wrong, token not attached | `task_retry` (owning task only) |
| `missing_feature` | entire loading state not implemented | `task_retry` |
| `spec_conflict` | implementation incompatible with spec interface | escalate → `blocked` |
| `architecture_error` | wrong pattern used entirely | escalate → `blocked` |
| `env_missing` | pytest not installed, node_modules missing, runtime service unavailable | CI only |

**Selection rule:** use the highest-severity fix path among all failed criteria.
Severity order: `blocked` > `task_retry` > `direct_fixup` > CI only.

**env_missing rule:** if ALL failures are `env_missing`, Claude must not reset any task. Claude writes a CI trigger note in `activity_log` and stops.
No `retry` metadata is written. No `retry_count` is incremented.

**fix_loop vs direct_fixup:** Use `fix_loop` instead of `direct_fixup` when
the fix spans more than two files or requires symbol-level deletion surgery
that is better delegated to Codex via patch tickets. For single-file or
trivial inline fixes, prefer `direct_fixup`.

### Required status.json writes on failure

Before resetting any task, Claude MUST write:

```json
"last_review_failure": {
  "review_task": "T05",
  "timestamp": "<ISO8601>",
  "fix_path": "task_retry",
  "failed_criteria": ["J8"],
  "failure_types": { "J8": "type_error" },
  "reset_scope": ["T03"],
  "do_not_touch": ["T01", "T02", "T04"],
  "fix_instructions": "exact actionable text per file and line"
}
```

`last_review_failure` is cleared (set to null) when the retried task reaches `done`.

For `fix_loop`, Claude must additionally write:

1. **Review task:** set `status` to `failed_review`; add `failed_review` object
   (`verdict`, `artifact`, `failed_criteria`, `timestamp`) and `blocked_by_fixes`
   list of pending ticket IDs.
2. **Each affected task:** add a `fix` sub-object with `status: "in_progress"`
   and a `tickets` array (see fix ticket schema in `conventions.md`).

`last_review_failure.fix_path` must be `"fix_loop"`. All other
`last_review_failure` fields follow the same rules as `task_retry`.
`last_review_failure` is cleared when all fix tickets reach `done` and the
review task is reset to `pending` for rerun.

---

## Downstream Impact Assessment

Runs after any `task_retry` completes. Does NOT run after `direct_fixup`
or `review_rerun`.

### Contract change detection

For each downstream task with `status=done`, Claude checks whether the
retried task changed any interface that the downstream task imports:
- Types in `frontend/types/`
- Function signatures in `lib/api/`
- API response shapes
- Error object shape (only if downstream parses error fields)

### Invalidation rules

| Change | Downstream action |
|---|---|
| Interface unchanged | Nothing — proceed to review directly |
| Error message format only | Nothing — proceed to review directly |
| Error object fields changed, downstream parses them | `direct_fixup` on downstream only |
| Function signature changed | `task_retry` on downstream only |
| Return type changed | `task_retry` on downstream only |
| Interface removed or renamed | `task_retry` on downstream + escalate |

Claude writes the assessment result into `last_review_failure`:

```json
"downstream_impact": {
  "assessed": true,
  "affected_tasks": [],
  "reason": "T03 fix changed only internal fetch logic. propertiesApi signatures unchanged. T04 is safe."
}
```

If `affected_tasks` is empty → proceed directly to review.
If `affected_tasks` is non-empty → resolve downstream first, then review.

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
- Claude may use `tools/status_guard.py` or `tools/run_task.sh` as orchestration helpers for these updates.
- Feature-level `status` in `status.json` transitions: `pending` → `in_progress` → `done` | `failed` | `blocked`
- Task-level `status` transitions: `pending` → `in_progress` → `done` | `failed` | `blocked`
- A feature is `done` only when `final-report.md` exists with disposition `accepted`.
- `final-report.md` is written only for final acceptance outcomes (accepted or failed after review), never for intermediate blocked states.
- `status.json` feature-level `status: "done"` means the workflow completed — it does not encode the acceptance verdict. The authoritative acceptance verdict is the `## Disposition:` line in `final-report.md` only. Do not manually add "ACCEPTED" entries to `activity_log` in `status.json`; the disposition belongs in `final-report.md` exclusively. There is no `accepted` status value in `status.json`.

### Runtime retry metadata

`status.json` may store runtime-only retry intent on a task:

```json
{
  "retry": {
    "type": "task_retry | direct_fixup | review_rerun",
    "reason": "short human-readable explanation",
    "scope": ["optional/path/glob"]
  }
}
```

Rules:
- Retry metadata belongs in `status.json`, not `tasks.md`
- Workers must treat retry metadata as authoritative for the current run
- Retry metadata is cleared automatically when the retried task reaches `done`
- A review task with verdict `FAIL` must block `next` until Claude explicitly
  chooses `task_retry` or `direct_fixup`

### Retry count and circuit breaker

Each task in `status.json` carries a `retry_count` field (default 0).
Claude increments `retry_count` on the task when fix path is `task_retry`.
`direct_fixup` and `review_rerun` do NOT increment `retry_count`.

Circuit breaker: if `retry_count >= 3` on any task → feature status → `blocked`
- Write blocker entry in `activity_log` with full history
- Do NOT reset the task to `pending`
- Do NOT invoke any worker
- Stop and wait for human resolution

### status.json edit discipline
- Only modify the exact fields required — never rewrite adjacent objects
- Never remove or reflow array structure
- `activity_log` is append-only: never delete or modify existing entries, always add a new entry at the end

### Verification output discipline
- Each table or section must appear exactly once
- No repeated blocks
- Stop after full coverage is achieved

### Document edit discipline (spec/tasks/acceptance)

When Claude edits spec.md, tasks.md, owner.md, or acceptance.md:

- Edits must be minimal-diff: modify only the necessary lines
- Never duplicate existing sections or rules
- Never re-insert content that already exists elsewhere in the document
- Each rule, bullet, or section must appear exactly once
- If a section is being refined, it must be edited in-place, not re-added

If duplication is detected:
- Claude must stop further edits
- Deduplicate the document before continuing

Edits are considered complete when:
- No repeated sections exist
- No semantic duplication exists
- Structure remains stable

### Edit completion rule

Claude must stop editing once all requested changes are applied.

Do NOT re-run the same modification logic multiple times.
Do NOT re-scan and re-apply identical patches.

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
- `env_missing` failures from review are CI-only events. Claude must not reset any task or increment `retry_count` for `env_missing` failures.

### Trigger Conditions
CI should be triggered:
- At feature completion (e.g. F0, F3, F7)
- Before final acceptance
- When integration-heavy features are introduced

---

## Autonomous Execution Protocol

When Claude is running as the orchestrator in an agentic session,
it executes the following loop without waiting for human input between steps:

1. Read `status.json` → find next `pending` task with all dependencies `done`
2. Invoke `tools/run_task.sh`
3. Read output artifact, update `status.json`
4. Append to `activity_log`
5. If review task just completed → execute failure classification and write `last_review_failure`
6. If `task_retry` just completed → run Downstream Impact Assessment
7. Return to step 1

### Automatic proceed (no human input needed)
- `env_missing` only: write CI note in `activity_log`, stop loop cleanly
- `direct_fixup`: apply fix, rerun review, continue
- `review_rerun`: rerun review, continue
- `fix_loop`: execute pending fix tickets sequentially via `run_fix_codex.sh`; update ticket status after each fix report; rerun review when `blocked_by_fixes` is empty; continue
- `task_retry` with `retry_count < 3`: invoke worker with retry context, continue

### Stop and confirm (show plan, wait for human "proceed")
- `task_retry` with `retry_count >= 3`: explain circuit breaker trigger, wait for human override
- `blocked` (spec_conflict or architecture_error): explain what decision is needed
- `final-report.md` written: show disposition, stop

### Retry context injection

Workers receive `last_review_failure` as part of their prompt on retry.
The wrapper script (`run_codex.sh`, `run_gemini.sh`) reads this field from
`status.json` and injects it at the top of the prompt before all other context.
If `last_review_failure` is null, no retry block is injected.

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
├── final-report.md           # Claude — final acceptance decision only
└── fix-reports/              # fix report artifacts (one per executed fix ticket)
    ├── fix-report-<ID>.md    # structured fix report (stdout from run_fix_codex.sh)
    └── fix-report-<ID>.log   # diagnostic log (stderr)
```

There are no global report files at the repo root. All artifacts are feature-scoped.
