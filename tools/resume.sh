#!/usr/bin/env bash
# tools/resume.sh — interactive single-step task runner
# Finds the current active feature and next task, asks for confirmation,
# runs exactly one task, then exits. Never auto-continues.
#
# Usage:
#   bash tools/resume.sh         — prompts for confirmation via /dev/tty
#   bash tools/resume.sh --run   — skips prompt, runs immediately
set -euo pipefail

RUN_MODE="${1:-}"

cd "$(dirname "$0")/.."

# ── Discover ─────────────────────────────────────────────────────────────────
OUTPUT=$(bash tools/next_feature.sh)
echo "$OUTPUT"

# Nothing to do
if echo "$OUTPUT" | grep -q "^All features complete"; then
    exit 0
fi

# ── Parse ────────────────────────────────────────────────────────────────────
FEATURE_DIR=$(echo "$OUTPUT" | grep '^Feature dir:' | sed 's/Feature dir:[[:space:]]*//')
NEXT_TASK_LINE=$(echo "$OUTPUT" | grep '^Next task:' | sed 's/Next task:[[:space:]]*//')

# A valid task ID matches T<digits> — anything else means blocked/failed/needs intervention
if [[ -z "$FEATURE_DIR" || ! "$NEXT_TASK_LINE" =~ ^T[0-9] ]]; then
    exit 0
fi

NEXT_TASK="$NEXT_TASK_LINE"

# ── Owner check: Claude-owned tasks must be run manually ─────────────────────
TASK_OWNER=$(echo "$OUTPUT" | grep '^Owner:' | sed 's/Owner:[[:space:]]*//')
if [[ "$TASK_OWNER" == "claude" ]]; then
    echo ""
    echo "Claude-owned task — must be run manually in Claude Code:"
    echo "  1. python3 tools/status_guard.py start $FEATURE_DIR $NEXT_TASK"
    echo "  2. Complete the task in Claude Code (read review.md, write final-report.md)"
    echo "  3. python3 tools/status_guard.py done  $FEATURE_DIR $NEXT_TASK"
    exit 0
fi

# ── Confirm ──────────────────────────────────────────────────────────────────
if [[ "$RUN_MODE" != "--run" ]]; then
    echo ""
    read -r -p "Run this task? [y/N] " CONFIRM </dev/tty
    if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# ── Execute one task, then stop ───────────────────────────────────────────────
echo ""
bash tools/run_task.sh "$FEATURE_DIR" "$NEXT_TASK"
