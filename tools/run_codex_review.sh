#!/usr/bin/env bash
# tools/run_codex_review.sh
# Run Codex review for a feature workspace.
# Usage: tools/run_codex_review.sh .ai/features/<feature> <task-id>
# Output: <feature>/review.md
# Log:    <feature>/codex-review.log
# NEVER modifies status.json.

set -euo pipefail

FEATURE_DIR="${1:-}"
TASK_ID="${2:-}"

if [[ -z "$FEATURE_DIR" || -z "$TASK_ID" ]]; then
  echo "Usage: $0 <feature-dir> <task-id>" >&2
  exit 1
fi

FEATURE_DIR="${FEATURE_DIR%/}"

for f in spec.md tasks.md owner.md acceptance.md; do
  if [[ ! -f "$FEATURE_DIR/$f" ]]; then
    echo "ERROR: missing required file: $FEATURE_DIR/$f" >&2
    exit 1
  fi
done

SPEC=$(cat "$FEATURE_DIR/spec.md")
TASKS=$(cat "$FEATURE_DIR/tasks.md")
OWNER=$(cat "$FEATURE_DIR/owner.md")
ACCEPTANCE=$(cat "$FEATURE_DIR/acceptance.md")
RETRY_BLOCK=$(python3 tools/status_guard.py task-retry-block "$FEATURE_DIR" "$TASK_ID")

CODEX_REPORT=""
if compgen -G "$FEATURE_DIR/codex-build-*.md" > /dev/null; then
  CODEX_REPORT=$(cat "$FEATURE_DIR"/codex-build-*.md)
fi

GEMINI_REPORT=""
if compgen -G "$FEATURE_DIR/gemini-build-*.md" > /dev/null; then
  GEMINI_REPORT=$(cat "$FEATURE_DIR"/gemini-build-*.md)
fi

# Extract activity_log from status.json
ACTIVITY_LOG=""
if [[ -f "$FEATURE_DIR/status.json" ]]; then
  ACTIVITY_LOG=$(python3 -c "
import json, sys
try:
    d = json.load(open('$FEATURE_DIR/status.json'))
    for e in d.get('activity_log', []):
        print(f\"{e.get('timestamp','?')} [{e.get('by','?')}] {e.get('event','')}\")
except Exception as ex:
    print(f'(could not parse activity_log: {ex})', file=sys.stderr)
")
fi

# Extract fix_loop authorized files from status.json T*.fix.tickets[].files
FIX_LOOP_SCOPE=""
if [[ -f "$FEATURE_DIR/status.json" ]]; then
  FIX_LOOP_SCOPE=$(python3 -c "
import json, sys
try:
    d = json.load(open('$FEATURE_DIR/status.json'))
    for t in d.get('tasks', []):
        fix = t.get('fix', {})
        for ticket in fix.get('tickets', []):
            tid = ticket.get('id','?')
            status = ticket.get('status','?')
            for f in ticket.get('files', []):
                print(f'{tid} ({status}): {f}')
except Exception as ex:
    print(f'(could not parse fix tickets: {ex})', file=sys.stderr)
")
fi

PROMPT="You are Codex, performing a code review for a completed feature.

## Your Review Role
- Validate the implementation against every acceptance criterion
- Identify gaps, bugs, missing tests, and boundary violations
- Check that business logic is NOT in frontend components
- Check that status.json was NOT modified by Codex or Gemini
- Check that all API types are published to frontend/types/
- Do NOT modify status.json
- Do NOT create or write review.md yourself. Any attempt to write report files directly is a contract violation.
- Output the review report ONLY to stdout.
- The wrapper script will capture stdout into the correct feature-scoped review.md.

## Scope Evaluation Rules (authoritative — override strict task manifest comparison)
- Files listed in the Fix Loop Authorized Files section below are APPROVED scope even if absent from the original task manifest. Do NOT flag them as boundary violations.
- If the Activity Log contains an entry recording a revert of a file change (e.g. \"reverted\", \"revert\"), treat that file as clean in the current working tree. Do NOT flag it as a scope violation.
- For A5: a human-verified pytest run recorded in the Activity Log (\"pytest\", \"passed\", exit code 0) is acceptable evidence. Do NOT require sandbox execution of pytest to pass A5.

## Feature Spec
$SPEC

## Tasks
$TASKS

## Acceptance Criteria
$ACCEPTANCE

## Codex Build Report
$CODEX_REPORT

## Gemini Build Report
$GEMINI_REPORT

## Owner Context
$OWNER

## Activity Log (authoritative runtime history — use to verify reverts and human verifications)
$ACTIVITY_LOG

## Fix Loop Authorized Files (treat as legitimate scope — do NOT flag as boundary violations)
$FIX_LOOP_SCOPE

## Task to Execute Now: $TASK_ID
Review all implementation artifacts against every acceptance criterion listed above.

$RETRY_BLOCK

Output a review report in this format:

# Review

## Verdict
PASS or FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| <criterion> | PASS/FAIL | <notes> |

## Issues Found
- list each issue with severity: BLOCKER / WARNING / MINOR

## Required Fixes
- list specific fixes required before acceptance (blockers only)

## Approved Items
- list items that are correctly implemented
"

REVIEW_FILE="$FEATURE_DIR/review.md"
LOG_FILE="$FEATURE_DIR/codex-review.log"

# Archive existing review + log before overwrite (consistent with .attempt-TIMESTAMP pattern)
if [[ -f "$REVIEW_FILE" || -f "$LOG_FILE" ]]; then
  ARCHIVE_TS=$(date -u +%Y%m%d-%H%M%S)
  [[ -f "$REVIEW_FILE" ]] && mv "$REVIEW_FILE" "$FEATURE_DIR/review.attempt-${ARCHIVE_TS}.md"
  [[ -f "$LOG_FILE"    ]] && mv "$LOG_FILE"    "$FEATURE_DIR/codex-review.attempt-${ARCHIVE_TS}.log"
  echo "Archived previous review  → review.attempt-${ARCHIVE_TS}.{md,log}"
fi

echo "Running codex review for: $FEATURE_DIR task=$TASK_ID"
echo "Review → $REVIEW_FILE"
echo "Log    → $LOG_FILE"

CODEX_FLAGS=(--skip-git-repo-check)
if [[ "${CODEX_BYPASS_SANDBOX:-0}" == "1" ]]; then
  CODEX_FLAGS+=(--dangerously-bypass-approvals-and-sandbox)
fi

codex exec "${CODEX_FLAGS[@]}" "$PROMPT" </dev/null \
  2> >(tee "$LOG_FILE" >&2) \
  | tee "$REVIEW_FILE"

EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "ERROR: codex review exited with code $EXIT_CODE. See $LOG_FILE" >&2
  exit $EXIT_CODE
fi

echo "Done. Review written to $REVIEW_FILE"
