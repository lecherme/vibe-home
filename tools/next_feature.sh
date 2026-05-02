#!/usr/bin/env bash
# tools/next_feature.sh — read-only: find active feature and next runnable task
# Outputs structured KEY: value lines suitable for both human reading and script parsing.
set -euo pipefail

cd "$(dirname "$0")/.."

ROADMAP=".ai/roadmap.md"
FEATURES_DIR=".ai/features"

# Emit feature dirs in roadmap order; fall back to lexicographic if roadmap unreadable.
_feature_dirs_ordered() {
    local ids
    ids=$(grep '^## F[0-9]' "$ROADMAP" 2>/dev/null | sed 's/^## //' | awk '{print $1}') || true

    if [[ -z "$ids" ]]; then
        echo "WARNING: roadmap unreadable — falling back to directory order" >&2
        find "$FEATURES_DIR" -maxdepth 1 -type d -name 'F[0-9]*' 2>/dev/null | sort
        return
    fi

    local any=false
    while IFS= read -r fid; do
        local dir
        dir=$(find "$FEATURES_DIR" -maxdepth 1 -type d -name "${fid}-*" 2>/dev/null | head -1)
        if [[ -n "$dir" ]]; then
            echo "$dir"
            any=true
        fi
    done <<< "$ids"

    if [[ "$any" == "false" ]]; then
        echo "WARNING: no dirs matched roadmap — falling back to directory order" >&2
        find "$FEATURES_DIR" -maxdepth 1 -type d -name 'F[0-9]*' 2>/dev/null | sort
    fi
}

# Find first non-done feature
ACTIVE_DIR=""
ACTIVE_STATUS=""

while IFS= read -r dir; do
    [[ -f "$dir/status.json" ]] || continue
    fstatus=$(python3 -c \
        "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('status',''))" \
        "$dir/status.json" 2>/dev/null) || continue
    if [[ "$fstatus" != "done" ]]; then
        ACTIVE_DIR="$dir"
        ACTIVE_STATUS="$fstatus"
        break
    fi
done < <(_feature_dirs_ordered)

if [[ -z "$ACTIVE_DIR" ]]; then
    echo "All features complete. Nothing to resume."
    exit 0
fi

FEATURE_NAME=$(basename "$ACTIVE_DIR")

# Validate status.json (capture output; suppress stderr into stdout for display)
VALIDATE_OUT=$(python3 tools/status_guard.py validate "$ACTIVE_DIR" 2>&1) \
    && VALIDATE_OK=0 || VALIDATE_OK=$?

# Next runnable task id (empty string if none)
NEXT_TASK=$(python3 tools/status_guard.py next "$ACTIVE_DIR" 2>/dev/null) || NEXT_TASK=""

# next_step hint for blocked/failed cases
NEXT_STEP=$(python3 -c \
    "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('next_step',''))" \
    "$ACTIVE_DIR/status.json" 2>/dev/null) || NEXT_STEP=""

TASK_TITLE=""
TASK_OWNER=""
if [[ -n "$NEXT_TASK" ]]; then
    # task-info returns: owner type status artifact
    TASK_OWNER=$(python3 tools/status_guard.py task-info "$ACTIVE_DIR" "$NEXT_TASK" \
        2>/dev/null | awk '{print $1}') || TASK_OWNER=""
    TASK_TITLE=$(python3 -c \
        "import json,sys; d=json.load(open(sys.argv[1])); \
t=next((t for t in d.get('tasks',[]) if t.get('id')==sys.argv[2]),None); \
print(t.get('title','') if t else '')" \
        "$ACTIVE_DIR/status.json" "$NEXT_TASK" 2>/dev/null) || TASK_TITLE=""
fi

# ── Output ──────────────────────────────────────────────────────────────────
echo "=== Next Feature ==="
echo "Feature:     $FEATURE_NAME"
echo "Feature dir: $ACTIVE_DIR"
echo "Status:      $ACTIVE_STATUS"

if [[ $VALIDATE_OK -eq 0 ]]; then
    echo "Validate:    ✓ status.json OK"
else
    echo "Validate:    ✗ errors found"
    echo "$VALIDATE_OUT" | sed 's/^/             /'
fi

echo ""

# ── Review failure summary (only when feature is in failed state) ────────────
if [[ "$ACTIVE_STATUS" == "failed" ]]; then
    REVIEW_SUMMARY=$(python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
lrf=d.get('last_review_failure')
if not lrf or not isinstance(lrf,dict):sys.exit(0)
out=[]
fp=lrf.get('fix_path')
if fp:out.append('  Fix path:         '+fp)
fc=lrf.get('failed_criteria')
if fc and isinstance(fc,list):out.append('  Failed criteria:  '+', '.join(str(x) for x in fc))
ft=lrf.get('failure_types')
if ft and isinstance(ft,dict):out.append('  Failure types:    '+', '.join(str(k)+': '+str(v) for k,v in ft.items()))
rs=lrf.get('reset_scope')
if rs and isinstance(rs,list):out.append('  Reset scope:      '+', '.join(str(x) for x in rs))
dnt=lrf.get('do_not_touch')
if dnt and isinstance(dnt,list):out.append('  Do not touch:     '+', '.join(str(x) for x in dnt))
fi=lrf.get('fix_instructions')
if fi:out.append('  Fix instructions: '+str(fi))
if out:print('Review failure summary:\n'+'\n'.join(out))
" "$ACTIVE_DIR/status.json" 2>/dev/null) || REVIEW_SUMMARY=""
    if [[ -n "$REVIEW_SUMMARY" ]]; then
        echo "$REVIEW_SUMMARY"
        echo ""
    fi
fi

if [[ -n "$NEXT_TASK" ]]; then
    echo "Next task:   $NEXT_TASK"
    [[ -n "$TASK_TITLE" ]] && echo "Title:       $TASK_TITLE"
    [[ -n "$TASK_OWNER" ]] && echo "Owner:       $TASK_OWNER"
    echo ""
    echo "Command:     bash tools/run_task.sh $ACTIVE_DIR $NEXT_TASK"
else
    echo "Next task:   (none)"
    [[ -n "$NEXT_STEP" ]] && echo "Hint:        $NEXT_STEP"
    echo ""
    echo "No runnable task. Manual intervention required."
fi
