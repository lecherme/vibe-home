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

## Idempotent Implementation Discipline
Before writing code:
- Inspect existing target files first.
- If a target file is missing, create it.
- If a target file exists and is clean but incomplete, patch it minimally.
- If a target file exists but contains duplicated blocks, conflicting logic, broken structure, or failed previous partial attempts, rewrite the affected file fully.
- Do not append duplicate functions, exports, routes, schemas, tests, or imports.
- Do not create alternative filenames such as *_v2, *_new, *_fixed, or duplicate test files.
- Keep file paths stable and task-scoped.
- Re-running this task should not introduce duplicate code or duplicate artifacts.
- When modifying existing code, preserve unrelated behavior.
- When adding to an existing registry/router/index file, check whether the entry already exists before adding it.

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

codex exec --skip-git-repo-check "$PROMPT" \
  2> >(tee "$LOG_FILE" >&2) \
  | tee "$REPORT_FILE"

EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "ERROR: codex exited with code $EXIT_CODE. See $LOG_FILE" >&2
  exit $EXIT_CODE
fi

echo "Done. Report written to $REPORT_FILE"
