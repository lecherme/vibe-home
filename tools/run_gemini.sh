#!/usr/bin/env bash
# tools/run_gemini.sh
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

TASK_BLOCK=$(awk -v tid="## $TASK_ID" '
  substr($0, 1, length(tid)) == tid { found=1; print; next }
  found && /^## T[0-9]/ { exit }
  found { print }
' "$FEATURE_DIR/tasks.md")

if [[ -z "$TASK_BLOCK" ]]; then
  echo "ERROR: task $TASK_ID not found in $FEATURE_DIR/tasks.md" >&2
  exit 1
fi

PROMPT="You are Gemini, a UI scaffolding and low-risk implementation worker.

You must directly create or update the required files in the repository.
Do not only output code blocks.
After modifying files, write the final report to:
.ai/features/F0-foundation/gemini-build-T03.md
Only modify files required by T03.

ABSOLUTE FILE WRITE RULES:
- You may ONLY create or update: frontend/app/page.tsx
- You must NOT modify any other file
- You must NOT modify .ai/, backend/, tools/, package files, config files, or status.json
- If you cannot comply, stop and report failure

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

## All Tasks (for context)
$TASKS

## Task to Execute Now: $TASK_ID
$TASK_BLOCK

## Owner Context
$OWNER

## Instructions
Implement ONLY the task above ($TASK_ID). Do not implement any other tasks.
When done, output a build report in this format:

# Gemini Build Report

## Task Completed
- $TASK_ID

## Components Created
- list each component file

## Pages Scaffolded
- list each page file

## Open Issues
- list any blockers or incomplete items
"

REPORT_FILE="$FEATURE_DIR/gemini-build-${TASK_ID}.md"
LOG_FILE="$FEATURE_DIR/gemini-build-${TASK_ID}.log"

NODE20="/Users/xiangzhifeng/.local/share/fnm/node-versions/v20.20.2/installation/bin/node"
GEMINI_BIN=$(which gemini)

echo "Running gemini for: $FEATURE_DIR task=$TASK_ID"
echo "Report → $REPORT_FILE"
echo "Log    → $LOG_FILE"

# --approval-mode plan = read-only, no file writes, no tool execution
"$NODE20" "$GEMINI_BIN" --approval-mode yolo -p "$PROMPT" \
  2> >(tee "$LOG_FILE" >&2) \
  | tee "$REPORT_FILE"

EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "ERROR: gemini exited with code $EXIT_CODE. See $LOG_FILE" >&2
  exit $EXIT_CODE
fi

echo "Done. Report written to $REPORT_FILE"