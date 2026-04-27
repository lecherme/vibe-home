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

echo "Running codex review for: $FEATURE_DIR task=$TASK_ID"
echo "Review → $REVIEW_FILE"
echo "Log    → $LOG_FILE"

codex exec --skip-git-repo-check "$PROMPT" \
  2> >(tee "$LOG_FILE" >&2) \
  | tee "$REVIEW_FILE"

EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "ERROR: codex review exited with code $EXIT_CODE. See $LOG_FILE" >&2
  exit $EXIT_CODE
fi

echo "Done. Review written to $REVIEW_FILE"
