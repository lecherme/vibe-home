#!/usr/bin/env bash
# tools/run_task.sh
# Usage: bash tools/run_task.sh .ai/features/F2-property-browsing T03

set -euo pipefail

FEATURE_DIR="${1:-}"
TASK_ID="${2:-}"

if [[ -z "$FEATURE_DIR" || -z "$TASK_ID" ]]; then
  echo "Usage: $0 <feature-dir> <task-id>" >&2
  exit 1
fi

STATUS_FILE="$FEATURE_DIR/status.json"
TASKS_FILE="$FEATURE_DIR/tasks.md"

if [[ ! -f "$STATUS_FILE" ]]; then
  echo "ERROR: missing status.json: $STATUS_FILE" >&2
  exit 1
fi

python3 -m json.tool "$STATUS_FILE" >/dev/null

OWNER=$(python3 - "$STATUS_FILE" "$TASK_ID" <<'PY'
import json, sys
status_file, task_id = sys.argv[1], sys.argv[2]
data = json.load(open(status_file))
for task in data["tasks"]:
    if task["id"] == task_id:
        print(task["owner"])
        sys.exit(0)
print(f"ERROR: task {task_id} not found", file=sys.stderr)
sys.exit(1)
PY
)

TASK_STATUS=$(python3 - "$STATUS_FILE" "$TASK_ID" <<'PY'
import json, sys
status_file, task_id = sys.argv[1], sys.argv[2]
data = json.load(open(status_file))
for task in data["tasks"]:
    if task["id"] == task_id:
        print(task["status"])
        sys.exit(0)
sys.exit(1)
PY
)

if [[ "$TASK_STATUS" != "pending" && "$TASK_STATUS" != "in_progress" ]]; then
  echo "ERROR: task $TASK_ID status is '$TASK_STATUS', refusing to rerun." >&2
  exit 1
fi

echo "=== Run Task ==="
echo "Feature: $FEATURE_DIR"
echo "Task:    $TASK_ID"
echo "Owner:   $OWNER"
echo "Status:  $TASK_STATUS"
echo ""

case "$OWNER" in
  codex)
    CMD=(bash tools/run_codex.sh "$FEATURE_DIR" "$TASK_ID")
    ;;
  gemini)
    CMD=(bash tools/run_gemini.sh "$FEATURE_DIR" "$TASK_ID")
    ;;
  claude)
    echo "ERROR: Claude-owned tasks are not executable via worker wrapper." >&2
    exit 1
    ;;
  *)
    echo "ERROR: unknown owner: $OWNER" >&2
    exit 1
    ;;
esac

echo "Command:"
printf ' %q' "${CMD[@]}"
echo ""
echo ""

read -p "Proceed? (y/n): " CONFIRM
if [[ "$CONFIRM" != "y" ]]; then
  echo "Aborted."
  exit 0
fi

"${CMD[@]}"

echo ""
echo "=== Done ==="
echo "Artifact should be under: $FEATURE_DIR"
echo "Now verify scope and update status.json via Claude/orchestrator."