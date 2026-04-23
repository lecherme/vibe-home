#!/usr/bin/env bash
# tools/run_codex.sh
# Run codex-owned tasks for a feature workspace.
# Usage: tools/run_codex.sh .ai/features/<feature>
# Output: <feature>/codex-build-report.md
# Log:    <feature>/codex-build.log
# NEVER modifies status.json.

set -euo pipefail

FEATURE_DIR="${1:-}"
if [[ -z "$FEATURE_DIR" ]]; then
  echo "Usage: $0 <feature-dir>" >&2
  exit 1
fi

FEATURE_DIR="${FEATURE_DIR%/}"  # strip trailing slash

for f in spec.md tasks.md owner.md; do
  if [[ ! -f "$FEATURE_DIR/$f" ]]; then
    echo "ERROR: missing required file: $FEATURE_DIR/$f" >&2
    exit 1
  fi
done

SPEC=$(cat "$FEATURE_DIR/spec.md")
TASKS=$(cat "$FEATURE_DIR/tasks.md")
OWNER=$(cat "$FEATURE_DIR/owner.md")

# Extract only codex-owned tasks from tasks.md (lines containing "owner: codex")
CODEX_TASKS=$(awk '
  /^##/ { task=$0; owner="" }
  /owner:[[:space:]]*codex/ { owner="codex" }
  owner=="codex" { print task; task=""; owner="" }
' "$FEATURE_DIR/tasks.md" 2>/dev/null || grep -i "owner.*codex\|codex.*owner" "$FEATURE_DIR/tasks.md" || echo "(see tasks.md for codex tasks)")

PROMPT="You are Codex, a backend and critical-logic implementation worker.

## Your Role Constraints
- Implement backend logic, FastAPI routers, services, schemas, ORM models, migrations
- Implement critical frontend logic: auth flow, API client layer (lib/api/)
- Do NOT implement UI layout, styling, or component structure
- Do NOT modify status.json
- Do NOT make product or architecture decisions
- Write tests for all service-layer functions
- At the end, write a codex-build-report.md summarizing: files changed, tests written, API types published, and any open issues

## Feature Spec
$SPEC

## All Tasks
$TASKS

## Your Tasks (codex-owned only)
$CODEX_TASKS

## Owner Context
$OWNER

## Instructions
Implement all codex-owned tasks listed above. Follow the spec and constraints exactly.
When done, output a build report in this format:

# Codex Build Report

## Tasks Completed
- list each task

## Files Changed
- list each file

## API Types Published
- list any types written to frontend/types/

## Tests Written
- list test files

## Open Issues
- list any blockers or incomplete items
"

REPORT_FILE="$FEATURE_DIR/codex-build-report.md"
LOG_FILE="$FEATURE_DIR/codex-build.log"

echo "Running codex for: $FEATURE_DIR"
echo "Report → $REPORT_FILE"
echo "Log    → $LOG_FILE"

codex exec --skip-git-repo-check "$PROMPT" \
  1>"$REPORT_FILE" \
  2>"$LOG_FILE"

EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "ERROR: codex exited with code $EXIT_CODE. See $LOG_FILE" >&2
  exit $EXIT_CODE
fi

echo "Done. Report written to $REPORT_FILE"
