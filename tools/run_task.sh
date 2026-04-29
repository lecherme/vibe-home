#!/usr/bin/env bash
# tools/run_task.sh
# Claude-owned task runner for worker tasks.
#
# Usage:
#   bash tools/run_task.sh .ai/features/F2-property-browsing T03
#
# This script may update status.json because it is an orchestration helper run by
# Claude Code. Codex/Gemini worker wrappers still must never modify status.json.

set -euo pipefail

FEATURE_DIR="${1:-}"
TASK_ID="${2:-}"

if [[ -z "$FEATURE_DIR" || -z "$TASK_ID" ]]; then
  echo "Usage: $0 <feature-dir> <task-id>" >&2
  exit 1
fi

cd "$(dirname "$0")/.."

echo "=== Run Task ==="
echo "Feature: $FEATURE_DIR"
echo "Task:    $TASK_ID"

python3 tools/status_guard.py preflight "$FEATURE_DIR" "$TASK_ID"
read OWNER TASK_TYPE TASK_STATUS EXPECTED_ARTIFACT < <(python3 tools/status_guard.py task-info "$FEATURE_DIR" "$TASK_ID")

echo "Owner:   $OWNER"
echo "Type:    $TASK_TYPE"
echo "Status:  $TASK_STATUS"
echo "Artifact target: $EXPECTED_ARTIFACT"

TASK_STARTED=false
TASK_DONE=false
SCOPE_BASELINE=""

on_error() {
  local exit_code=$?
  if [[ -n "$SCOPE_BASELINE" && -f "$SCOPE_BASELINE" ]]; then
    rm -f "$SCOPE_BASELINE"
  fi
  if [[ "$TASK_STARTED" == "true" && "$TASK_DONE" != "true" ]]; then
    # False-failure detection: non-review task whose artifact exists and passes validate-artifact
    # enters needs_verification so Claude can decide; all other failures mark failed directly.
    if [[ -n "$TASK_TYPE" && "$TASK_TYPE" != "review" ]] && \
       python3 tools/status_guard.py validate-artifact "$FEATURE_DIR" "$TASK_ID" 2>/dev/null; then
      python3 tools/status_guard.py needs-verification "$FEATURE_DIR" "$TASK_ID" \
        "worker exited $exit_code but artifact passed validate-artifact" "$exit_code" || true
      echo "⚠️  Task $TASK_ID needs Claude verification — worker exited $exit_code but artifact exists and passed validate-artifact" >&2
    else
      python3 tools/status_guard.py fail "$FEATURE_DIR" "$TASK_ID" "run_task failed with exit code $exit_code" || true
    fi
  fi
  exit "$exit_code"
}
trap on_error ERR

python3 tools/status_guard.py start "$FEATURE_DIR" "$TASK_ID"
TASK_STARTED=true
SCOPE_BASELINE=$(mktemp)
{
  git diff --name-only
  git diff --name-only --cached
  git ls-files --others --exclude-standard
} | sort -u > "$SCOPE_BASELINE"

case "$OWNER:$TASK_TYPE" in
  codex:review)
    bash tools/run_codex_review.sh "$FEATURE_DIR" "$TASK_ID"
    ;;
  codex:*)
    bash tools/run_codex.sh "$FEATURE_DIR" "$TASK_ID"
    ;;
  gemini:*)
    bash tools/run_gemini.sh "$FEATURE_DIR" "$TASK_ID"
    ;;
  *)
    echo "ERROR: unsupported executable task owner/type: $OWNER/$TASK_TYPE" >&2
    exit 1
    ;;
esac

python3 tools/status_guard.py check-scope "$FEATURE_DIR" "$TASK_ID" "$SCOPE_BASELINE"
rm -f "$SCOPE_BASELINE"
SCOPE_BASELINE=""

python3 tools/status_guard.py done "$FEATURE_DIR" "$TASK_ID"
TASK_DONE=true

if ! bash tools/git_checkpoint.sh true false "$FEATURE_DIR"; then
  echo "WARNING: checkpoint failed after task completion; status.json remains done." >&2
fi

echo "✅ Task $TASK_ID complete"
