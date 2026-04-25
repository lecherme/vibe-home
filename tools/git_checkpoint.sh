#!/usr/bin/env bash
AUTO_COMMIT=${1:-false}
AUTO_PUSH=${2:-false}
set -e

echo "=== Git Checkpoint ==="

# 1. 状态检查
echo "[1] git status"
git status --short

echo ""
echo "[2] git diff summary"
git diff --stat

# 2. 检查 status.json（如果存在）
STATUS_FILE=$(find .ai/features -name "status.json" | head -n 1)

if [ -n "$STATUS_FILE" ]; then
  echo ""
  echo "[3] Validating status.json: $STATUS_FILE"
  python3 -m json.tool "$STATUS_FILE" >/dev/null && echo "✅ status.json valid" || {
    echo "❌ status.json invalid"
    exit 1
  }
fi

# 3. 防止危险文件
echo ""
echo "[4] Checking for forbidden files..."
FORBIDDEN=$(git status --porcelain | grep -E '\.env|node_modules|\.next|\.venv|\.log' || true)

if [ -n "$FORBIDDEN" ]; then
  echo "❌ Found forbidden files staged or modified:"
  echo "$FORBIDDEN"
  exit 1
fi

# 4. 自动生成 commit message（简单版）
FEATURE=$(jq -r '.feature' "$STATUS_FILE" 2>/dev/null || echo "unknown-feature")
STAGE=$(jq -r '.current_stage' "$STATUS_FILE" 2>/dev/null || echo "unknown-stage")

COMMIT_MSG="feat(${FEATURE}): checkpoint at ${STAGE}"

echo ""
echo "[5] Proposed commit message:"
echo "$COMMIT_MSG"

# 5. 确认 commit
if [ "$AUTO_COMMIT" = "true" ]; then
  CONFIRM="y"
else
  read -p "Proceed with commit? (y/n): " CONFIRM
fi

if [ "$CONFIRM" != "y" ]; then
  echo "Aborted."
  exit 0
fi

# 6. 执行 commit
git add .
git commit -m "$COMMIT_MSG"

echo "✅ Commit done."

# 7. 是否 push
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