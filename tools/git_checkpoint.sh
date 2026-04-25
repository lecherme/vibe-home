#!/usr/bin/env bash
AUTO_COMMIT=${1:-false}
AUTO_PUSH=${2:-false}
set -euo pipefail

echo "=== Git Checkpoint ==="

if ! command -v jq >/dev/null 2>&1; then
  echo "❌ jq is not installed."
  echo "Install it with:"
  echo "  macOS: brew install jq"
  echo "  Ubuntu: sudo apt-get install jq"
  exit 1
fi

echo "[1] git status"
git status --short

echo ""
echo "[2] git diff summary"
git diff --stat

STATUS_FILE=$(find .ai/features -name "status.json" -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null | head -n 1 || true)

if [ -n "$STATUS_FILE" ]; then
  echo ""
  echo "[3] Validating status.json: $STATUS_FILE"
  python3 -m json.tool "$STATUS_FILE" >/dev/null
  echo "✅ status.json valid"
else
  echo "⚠️ No status.json found. Commit message will use unknown-feature."
fi

FEATURE="unknown-feature"
STAGE="unknown-stage"

if [ -n "$STATUS_FILE" ]; then
  FEATURE=$(jq -r '.feature // "unknown-feature"' "$STATUS_FILE")
  STAGE=$(jq -r '.current_stage // "unknown-stage"' "$STATUS_FILE")
fi

COMMIT_MSG="feat(${FEATURE}): checkpoint at ${STAGE}"

echo ""
echo "[4] Proposed commit message:"
echo "$COMMIT_MSG"

if [ "$AUTO_COMMIT" = "true" ]; then
  CONFIRM="y"
else
  read -p "Proceed with commit? (y/n): " CONFIRM
fi

if [ "$CONFIRM" != "y" ]; then
  echo "Aborted."
  exit 0
fi

git add .

echo ""
echo "[5] Checking staged files for forbidden paths..."
FORBIDDEN=$(git diff --cached --name-only | grep -E '(^|/)(\.env($|\.)|node_modules/|\.next/|\.venv/|venv/|.*\.log$)' || true)

if [ -n "$FORBIDDEN" ]; then
  echo "❌ Found forbidden staged files:"
  echo "$FORBIDDEN"
  echo "Unstage them manually, then rerun."
  exit 1
fi

git commit -m "$COMMIT_MSG"
echo "✅ Commit done."

if [ "$AUTO_PUSH" = "true" ]; then
  PUSH_CONFIRM="y"
else
  read -p "Push to remote? (y/n): " PUSH_CONFIRM
fi

if [ "$PUSH_CONFIRM" = "y" ]; then
  git push
  echo "🚀 Pushed."
else
  echo "Skipped push."
fi