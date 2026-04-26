#!/usr/bin/env bash
AUTO_COMMIT=${1:-false}
AUTO_PUSH=${2:-false}
FEATURE_DIR=${3:-}
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

if [ -n "$FEATURE_DIR" ]; then
  STATUS_FILE="$FEATURE_DIR/status.json"
else
  STATUS_FILE=$(find .ai/features -name "status.json" -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null | head -n 1 || true)
fi

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

echo ""
echo "[5] Checking changed files before staging..."
set +e
python3 - <<'PY'
import re
import subprocess
import sys

forbidden_re = re.compile(r'(^|/)(\.env($|\.)|node_modules/|\.next/|\.venv/|venv/|.*\.log$)')

def lines(cmd):
    out = subprocess.check_output(cmd, text=True)
    return [line for line in out.splitlines() if line]

changed = set(lines(["git", "diff", "--name-only"]))
changed.update(lines(["git", "diff", "--name-only", "--cached"]))
changed.update(lines(["git", "ls-files", "--others", "--exclude-standard"]))

if not changed:
    print("No changed files to stage.")
    sys.exit(2)

forbidden = sorted(path for path in changed if forbidden_re.search(path))
if forbidden:
    print("Found forbidden changed files; nothing was staged:", file=sys.stderr)
    for path in forbidden:
        print(f"- {path}", file=sys.stderr)
    sys.exit(1)

subprocess.run(["git", "add", "--", *sorted(changed)], check=True)
print(f"Staged {len(changed)} changed file(s).")
PY
STAGE_RESULT=$?
set -e
if [ "$STAGE_RESULT" = "2" ]; then
  exit 0
elif [ "$STAGE_RESULT" != "0" ]; then
  exit "$STAGE_RESULT"
fi

echo ""
echo "[6] Checking staged files for forbidden paths..."
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
  git push
  echo "🚀 Pushed."
else
  echo "Skipped push."
fi
