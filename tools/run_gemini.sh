#!/usr/bin/env bash
# tools/run_gemini.sh
# Run a single gemini-owned task for a feature workspace.
# Usage: tools/run_gemini.sh .ai/features/<feature> <task-id>
# Output: <feature>/gemini-build-<TASK_ID>.md  (wrapper captures stdout)
# Log:    <feature>/gemini-build-<TASK_ID>.log (stderr)
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
Only modify files explicitly allowed by the current task block ($TASK_ID).

ABSOLUTE FILE WRITE RULES:
- You may ONLY create or update files explicitly listed in the current task block.
- You must NOT modify .ai/, backend/, tools/, package files, config files, or status.json unless the current task explicitly allows it.
- You must NOT modify any other file.
- If you cannot comply, stop and report failure.

## Your Role Constraints
- Implement page scaffolding, layout composition, feature components
- Implement CRUD views wired to existing API types
- Implement form handling using existing validation schemas
- Do NOT implement business logic in components
- Do NOT call Supabase directly from frontend code
- Do NOT modify lib/api/ or lib/auth/ (Codex owns these)
- Do NOT create new API endpoints or modify backend schemas
- Do NOT modify status.json
- Do NOT create or write report files yourself. Any attempt to write report files directly is a contract violation.
- Output the build report ONLY to stdout.
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
- Inspect existing files first

File handling rules:
- If file does not exist → create it
- If file exists and is clean but incomplete → patch minimally
- If file exists but is broken, duplicated, or inconsistent → rewrite the file cleanly

Strict anti-duplication rules:
- Do NOT create duplicate components (e.g., PropertyList2, PropertyListNew)
- Do NOT duplicate pages or routes
- Do NOT duplicate imports
- Do NOT duplicate hooks or state logic
- Do NOT create alternative filenames

Next.js structure safety:
- Respect existing app/ or pages/ routing structure
- Do NOT break layout.tsx hierarchy
- When modifying layout/page, preserve existing structure unless task explicitly requires change

Component discipline:
- Keep components small and composable
- Reuse existing components if present
- Do NOT inline large logic blocks into pages

Re-run safety:
- Re-running this task must NOT introduce duplicated UI, routes, or components
- Changes must be deterministic and stable

## stdout / stderr discipline — CRITICAL
- Your stdout is captured DIRECTLY as the artifact file by the wrapper script.
- stdout must contain ONLY the final # Gemini Build Report block — nothing else.
- Do NOT print any reasoning, planning, progress notes, tool call descriptions,
  file read summaries, or intermediate analysis to stdout.
- All thinking, exploration notes, and execution logs must go to stderr only.
- The artifact validation will FAIL and the task will be marked failed if stdout
  contains anything before '# Gemini Build Report'.
- EXCEPTION: verification results (tsc exit code, error summary) are evidence,
  not execution logs — they belong in the report (stdout), not in stderr.

## Verification Requirements (MANDATORY)
Before writing the build report you MUST run the TypeScript compiler check:

  cd frontend && npx tsc --noEmit 2>&1

Record in ## Verification:
- The exact command you ran
- The exit code
- If exit 0: write: exit 0 — no errors
- If exit non-zero: write a short summary of the key errors (file, line, message);
  do NOT paste the full raw output verbatim

If tsc reports errors, still complete the ## Verification section and also list
the errors in ## Open Issues. Do not skip verification or suppress results.

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

## Verification
- Command: \`cd frontend && npx tsc --noEmit\`
- Result: [exit 0 — no errors] or [exit 1 — summary of key errors]
- Smoke: [optional: brief description of any quick runtime check performed]

## Open Issues
- list any blockers, tsc errors, or incomplete items; or 'None'
"

REPORT_FILE="$FEATURE_DIR/gemini-build-${TASK_ID}.md"
LOG_FILE="$FEATURE_DIR/gemini-build-${TASK_ID}.log"

GEMINI_BIN=$(which gemini)
# Gemini CLI requires Node >=20. Resolve the fnm v20 node explicitly so this
# script works regardless of which Node version the parent shell activated.
NODE_BIN=$(fnm exec --using=v20 node --print-eval "process.execPath" 2>/dev/null || true)
if [[ -z "$NODE_BIN" ]]; then
  NODE_BIN=$(ls "$HOME/.local/share/fnm/node-versions/v20."*/installation/bin/node 2>/dev/null | tail -1)
fi

echo "Running gemini for: $FEATURE_DIR task=$TASK_ID"
echo "Report → $REPORT_FILE"
echo "Log    → $LOG_FILE"

# --approval-mode yolo allows Gemini to apply permitted UI edits; post-run diff review is required.
"$NODE_BIN" "$GEMINI_BIN" --approval-mode yolo -p "$PROMPT" \
  2> >(tee "$LOG_FILE" >&2) \
  | awk '/^# Gemini Build Report/{found=1} found{print}' \
  | tee "$REPORT_FILE"

EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "ERROR: gemini exited with code $EXIT_CODE. See $LOG_FILE" >&2
  exit $EXIT_CODE
fi

echo "Done. Report written to $REPORT_FILE"
