#!/usr/bin/env bash
# tools/run_gemini.sh
# Run gemini-owned tasks for a feature workspace.
# Usage: tools/run_gemini.sh .ai/features/<feature>
# Output: <feature>/gemini-build-report.md
# Log:    <feature>/gemini-build.log
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

# Extract only gemini-owned tasks from tasks.md (lines containing "owner: gemini")
GEMINI_TASKS=$(awk '
  /^##/ { task=$0; owner="" }
  /owner:[[:space:]]*gemini/ { owner="gemini" }
  owner=="gemini" { print task; task=""; owner="" }
' "$FEATURE_DIR/tasks.md" 2>/dev/null || grep -i "owner.*gemini\|gemini.*owner" "$FEATURE_DIR/tasks.md" || echo "(see tasks.md for gemini tasks)")

PROMPT="You are Gemini, a UI scaffolding and low-risk implementation worker.

## Your Role Constraints
- Implement page scaffolding, layout composition, feature components
- Implement CRUD views wired to existing API types
- Implement form handling using existing validation schemas
- Do NOT implement business logic in components
- Do NOT call Supabase directly from frontend code
- Do NOT modify lib/api/ or lib/auth/ (Codex owns these)
- Do NOT create new API endpoints or modify backend schemas
- Do NOT modify status.json
- At the end, write a gemini-build-report.md summarizing: components created, pages scaffolded, and any open issues

## Feature Spec
$SPEC

## All Tasks
$TASKS

## Your Tasks (gemini-owned only)
$GEMINI_TASKS

## Owner Context
$OWNER

## Instructions
Implement all gemini-owned tasks listed above. Follow the spec and constraints exactly.
When done, output a build report in this format:

# Gemini Build Report

## Tasks Completed
- list each task

## Components Created
- list each component file

## Pages Scaffolded
- list each page file

## Open Issues
- list any blockers or incomplete items
"

REPORT_FILE="$FEATURE_DIR/gemini-build-report.md"
LOG_FILE="$FEATURE_DIR/gemini-build.log"

NODE20="/Users/xiangzhifeng/.local/share/fnm/node-versions/v20.20.2/installation/bin/node"
GEMINI_BIN=$(which gemini)

echo "Running gemini for: $FEATURE_DIR"
echo "Report → $REPORT_FILE"
echo "Log    → $LOG_FILE"

"$NODE20" "$GEMINI_BIN" -p "$PROMPT" \
  1>"$REPORT_FILE" \
  2>"$LOG_FILE"

EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "ERROR: gemini exited with code $EXIT_CODE. See $LOG_FILE" >&2
  exit $EXIT_CODE
fi

echo "Done. Report written to $REPORT_FILE"
