#!/usr/bin/env bash
# tools/run_codex.sh
# Run a single codex-owned task for a feature workspace.
# Usage: tools/run_codex.sh .ai/features/<feature> <task-id>
# Output: <feature>/codex-build-<TASK_ID>.md  (wrapper captures stdout)
# Log:    <feature>/codex-build-<TASK_ID>.log (stderr)
# NEVER modifies status.json.

set -euo pipefail

FEATURE_DIR="${1:-}"
TASK_ID="${2:-}"

if [[ -z "$FEATURE_DIR" || -z "$TASK_ID" ]]; then
  echo "Usage: $0 <feature-dir> <task-id>" >&2
  exit 1
fi

FEATURE_DIR="${FEATURE_DIR%/}"

for f in spec.md tasks.md owner.md; do
  if [[ ! -f "$FEATURE_DIR/$f" ]]; then
    echo "ERROR: missing required file: $FEATURE_DIR/$f" >&2
    exit 1
  fi
done

SPEC=$(cat "$FEATURE_DIR/spec.md")
TASKS=$(cat "$FEATURE_DIR/tasks.md")
OWNER=$(cat "$FEATURE_DIR/owner.md")
RETRY_BLOCK=$(python3 tools/status_guard.py task-retry-block "$FEATURE_DIR" "$TASK_ID")

# Extract only the requested task block from tasks.md
# A task block starts at "## T<id>" and ends before the next "## T" or EOF
TASK_BLOCK=$(awk -v tid="## $TASK_ID" '
  substr($0, 1, length(tid)) == tid { found=1; print; next }
  found && /^## T[0-9]/ { exit }
  found { print }
' "$FEATURE_DIR/tasks.md")

if [[ -z "$TASK_BLOCK" ]]; then
  echo "ERROR: task $TASK_ID not found in $FEATURE_DIR/tasks.md" >&2
  exit 1
fi

PROMPT="You are Codex, a backend and critical-logic implementation worker.

## Your Role Constraints
- Implement backend logic, FastAPI routers, services, schemas, ORM models, migrations
- Implement critical frontend logic: auth flow, API client layer (lib/api/)
- Do NOT implement UI layout, styling, or component structure
- Do NOT modify status.json
- Do NOT make product or architecture decisions
- Write tests for all service-layer functions
- Do NOT create or write any report files yourself. Any attempt to write report files directly is a contract violation.
- Do NOT create codex-build-report.md.
- Do NOT create files at repo root unless the current task explicitly requires it.
- Your final answer on stdout must be the build report.
- The wrapper script will capture stdout into the correct feature-scoped artifact.

## Feature Spec
$SPEC

## All Tasks (for context)
$TASKS

## Task to Execute Now: $TASK_ID
$TASK_BLOCK

$RETRY_BLOCK

## Owner Context
$OWNER

## Scope-Gated Minimal-Diff Discipline

This discipline takes precedence over any judgment call to improve, refactor, or extend code beyond task scope.

### 1. Scope Gate (highest priority)
- You may ONLY modify, create, or delete files explicitly listed in this task's **Scope** block above.
- If a required change touches ANY file not on that list:
  - Do NOT modify the file.
  - Write the blocker in ## Open Issues with the exact filename and reason.
  - Stop. Do not continue past this blocker.
  - Do not expand scope unilaterally.

Exception — Registration-only additions:
If the out-of-scope file is a barrel/index export file, a route registry file, or an i18n translation file,
AND the entire change is (a) purely additive — no deletions, no logic changes — and (b) ≤ 3 lines total,
you MAY apply the change without stopping.
You MUST log it in ## Files Changed with tag \"(registration-only exemption)\".
All other out-of-scope modifications still require immediate stop + blocker.

### 2. Minimal Diff
- Patch existing files in-place. Do not rewrite whole files.
- A full-file rewrite is permitted ONLY when a targeted patch is structurally impossible
  (file corrupted, or contains irreconcilable duplication from a previous failed attempt).
  If you rewrite a file, state the justification explicitly in ## Open Issues.
- Do not rename identifiers, reorder imports, adjust formatting, or reorganize code
  outside the lines required to complete the task.
- Do not refactor, clean up, or improve code that is outside the task's Done condition.
- Do not add new directories, rename files, or change module organization unless
  the task explicitly requires it.

### 3. Idempotent Implementation
- Inspect existing target files before writing.
- If a file is missing, create it.
- If a file exists and is incomplete, patch it minimally (§2 above).
- Do not append duplicate functions, exports, routes, schemas, tests, or imports.
- Do not create alternative filenames such as *_v2, *_new, *_fixed, or duplicate test files.
- Keep file paths stable and task-scoped.
- Re-running this task must not introduce duplicate code or duplicate artifacts.
- When modifying existing code, preserve unrelated behavior.
- When adding to an existing registry/router/index file, check whether the entry already exists before adding it.

### 4. Reporting
- Every file modified, created, or deleted must appear in ## Files Changed.
- Files inspected but not changed must NOT appear in ## Files Changed.

## Instructions
Implement ONLY the task above ($TASK_ID). Do not implement any other tasks.
When done, output a build report in this format:

# Codex Build Report

## Task Completed
- $TASK_ID

## Files Changed
- list each file

## API Types Published
- list any types written to frontend/types/

## Tests Written
- list test files

## Open Issues
- list any blockers or incomplete items
"

REPORT_FILE="$FEATURE_DIR/codex-build-${TASK_ID}.md"
LOG_FILE="$FEATURE_DIR/codex-build-${TASK_ID}.log"

echo "Running codex for: $FEATURE_DIR task=$TASK_ID"
echo "Report → $REPORT_FILE"
echo "Log    → $LOG_FILE"

CODEX_FLAGS=(--skip-git-repo-check)
if [[ "${CODEX_BYPASS_SANDBOX:-0}" == "1" ]]; then
  CODEX_FLAGS+=(--dangerously-bypass-approvals-and-sandbox)
fi
if [[ -n "${CODEX_MODEL:-}" ]]; then
  CODEX_FLAGS+=(-m "$CODEX_MODEL")
fi

codex exec "${CODEX_FLAGS[@]}" "$PROMPT" \
  2> >(tee "$LOG_FILE" >&2) \
  | tee "$REPORT_FILE"

EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "ERROR: codex exited with code $EXIT_CODE. See $LOG_FILE" >&2
  exit $EXIT_CODE
fi

echo "Done. Report written to $REPORT_FILE"
