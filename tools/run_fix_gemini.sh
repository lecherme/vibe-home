#!/usr/bin/env bash
# tools/run_fix_gemini.sh
# Execute a single fix ticket via Gemini (patch-only mode).
# Usage: tools/run_fix_gemini.sh .ai/features/<feature> <ticket-id>
# Report: <feature>/fix-reports/fix-report-<TICKET_ID>.md  (stdout + verification)
# Log:    <feature>/fix-reports/fix-report-<TICKET_ID>.log (stderr)
# NEVER modifies status.json. Claude is the sole status.json owner.

set -euo pipefail

FEATURE_DIR="${1:-}"
TICKET_ID="${2:-}"

if [[ -z "$FEATURE_DIR" || -z "$TICKET_ID" ]]; then
  echo "Usage: $0 <feature-dir> <ticket-id>" >&2
  exit 1
fi

FEATURE_DIR="${FEATURE_DIR%/}"
STATUS_FILE="$FEATURE_DIR/status.json"

if [[ ! -f "$STATUS_FILE" ]]; then
  echo "ERROR: $STATUS_FILE not found" >&2
  exit 1
fi

# --- Extract ticket from status.json ---
TICKET_JSON=$(FEATURE_DIR="$FEATURE_DIR" TICKET_ID="$TICKET_ID" python3 <<'PYEOF'
import json, sys, os
feature_dir = os.environ["FEATURE_DIR"]
ticket_id   = os.environ["TICKET_ID"]
with open(f"{feature_dir}/status.json") as f:
    status = json.load(f)
ticket = next(
    (t for task in status.get("tasks", [])
       for t in task.get("fix", {}).get("tickets", [])
       if t["id"] == ticket_id),
    None
)
if not ticket:
    sys.stderr.write(f"ERROR: ticket '{ticket_id}' not found in {feature_dir}/status.json\n")
    sys.exit(1)
print(json.dumps(ticket))
PYEOF
)

# Helpers: extract fields from TICKET_JSON
field() {
  echo "$TICKET_JSON" | python3 -c \
    "import json,sys; v=json.load(sys.stdin).get('$1'); print(v if v is not None else '')"
}
files_inline() {
  echo "$TICKET_JSON" | python3 -c \
    "import json,sys; print(', '.join(json.load(sys.stdin).get('files',[])))"
}
files_list() {
  echo "$TICKET_JSON" | python3 -c \
    "import json,sys; [print(f'- {f}') for f in json.load(sys.stdin).get('files',[])]"
}

TICKET_STATUS=$(field status)
TICKET_REQUIRED_BY=$(field required_by)
TICKET_AFFECTED_TASK=$(field affected_task)
TICKET_AFFECTED_TASK_TITLE=$(field affected_task_title)
TICKET_CRITERION=$(field criterion)
TICKET_DESCRIPTION=$(field description)
TICKET_VERIFICATION=$(field verification)
TICKET_FILES_INLINE=$(files_inline)
TICKET_FILES_LIST=$(files_list)

# --- Guard: only run pending tickets ---
if [[ "$TICKET_STATUS" != "pending" ]]; then
  echo "ERROR: ticket '$TICKET_ID' has status '$TICKET_STATUS' (expected 'pending'). Aborting." >&2
  exit 1
fi

# --- Prepare output paths ---
FIX_REPORTS_DIR="$FEATURE_DIR/fix-reports"
mkdir -p "$FIX_REPORTS_DIR"
REPORT_FILE="$FIX_REPORTS_DIR/fix-report-${TICKET_ID}.md"
LOG_FILE="$FIX_REPORTS_DIR/fix-report-${TICKET_ID}.log"

# Archive existing report/log if present
if [[ -f "$REPORT_FILE" || -f "$LOG_FILE" ]]; then
  ARCHIVE_TS=$(date -u +%Y%m%d-%H%M%S)
  ARCHIVE_BASE="$FIX_REPORTS_DIR/fix-report-${TICKET_ID}.attempt-${ARCHIVE_TS}"
  [[ -f "$REPORT_FILE" ]] && mv "$REPORT_FILE" "${ARCHIVE_BASE}.md"
  [[ -f "$LOG_FILE"    ]] && mv "$LOG_FILE"    "${ARCHIVE_BASE}.log"
  echo "Archived existing report  → ${ARCHIVE_BASE}.{md,log}"
fi

GEMINI_TMP=$(mktemp)
trap 'rm -f "$GEMINI_TMP"' EXIT

echo "Running fix ticket  : $TICKET_ID"
echo "Criterion           : $TICKET_CRITERION"
echo "Report              → $REPORT_FILE"
echo "Log                 → $LOG_FILE"

# --- Build patch-only prompt ---
PROMPT="You are Gemini, executing a patch-only fix ticket.

## Fix Ticket
- ID: $TICKET_ID
- Review Task: $TICKET_REQUIRED_BY
- Affected Task: $TICKET_AFFECTED_TASK — $TICKET_AFFECTED_TASK_TITLE
- Criterion: $TICKET_CRITERION
- Description: $TICKET_DESCRIPTION

## Allowed Files (strict scope)
$TICKET_FILES_LIST

## Patch-Only Constraints
- Modify ONLY the files listed above. Any change to an unlisted file is a
  contract violation: record it in ## Open Issues and stop immediately.
- Delete or replace the problem symbols described. Do NOT add new features,
  refactor unrelated code, extend interfaces, or reorganize imports beyond
  what the fix requires.
- Do NOT create, rename, or move any file outside the declared scope.
- Do NOT modify status.json.
- Do NOT create or write any report files yourself. The wrapper captures stdout.

## stdout / stderr discipline — CRITICAL
- stdout must contain ONLY the final # Fix Report block — nothing else.
- Do NOT print any reasoning, planning, progress notes, tool call descriptions,
  file read summaries, or intermediate analysis to stdout.
- All thinking and exploration must go to stderr only.
- The artifact validation will FAIL if stdout contains anything before '# Fix Report:'.

## Output Format
Output a fix report in the format below.
Do NOT include a ## Verification section — the wrapper runs the verification
command and appends the result.

# Fix Report: $TICKET_ID

## Ticket Info
- **Review Task:** $TICKET_REQUIRED_BY
- **Affected Task:** $TICKET_AFFECTED_TASK — $TICKET_AFFECTED_TASK_TITLE
- **Criterion:** $TICKET_CRITERION
- **Files Declared:** $TICKET_FILES_INLINE

## Files Changed
- list each file actually modified (omit files inspected but not changed)

## Patch Summary
One to three sentences: what was deleted or replaced, and where.

## Open Issues
None, or list any remaining concerns or contract violations for Claude to evaluate.
"

# --- Resolve Node binary (same logic as run_gemini.sh) ---
GEMINI_BIN=$(which gemini)
NODE_BIN=$(fnm exec --using=v20 node --print-eval "process.execPath" 2>/dev/null || true)
if [[ -z "$NODE_BIN" ]]; then
  NODE_BIN=$(ls "$HOME/.local/share/fnm/node-versions/v20."*/installation/bin/node 2>/dev/null | tail -1 || true)
fi
if [[ -z "$NODE_BIN" ]]; then
  NODE_BIN=$(which node)
fi

# --- Run Gemini (capture stdout to temp; tee stderr to log) ---
set +e
"$NODE_BIN" "$GEMINI_BIN" --approval-mode yolo -p "$PROMPT" \
  2> >(tee "$LOG_FILE" >&2) \
  | awk '/^# Fix Report:/{found=1} found{print}' \
  > "$GEMINI_TMP"
GEMINI_EXIT=$?
set -e

# --- Run verification (always runs, even if Gemini failed) ---
VERIFY_EXIT=0
VERIFY_OUTPUT=""
if [[ -n "$TICKET_VERIFICATION" ]]; then
  set +e
  VERIFY_OUTPUT=$(bash -c "$TICKET_VERIFICATION" 2>&1)
  VERIFY_EXIT=$?
  set -e
else
  VERIFY_OUTPUT="(no verification command defined)"
  VERIFY_EXIT=1
fi

if [[ $VERIFY_EXIT -eq 0 ]]; then
  VERIFY_RESULT="**PASS**"
else
  VERIFY_RESULT="**FAIL**"
fi
VERIFY_OUTPUT_SHORT=$(echo "$VERIFY_OUTPUT" | head -1 | cut -c1-100)

# --- Write final report: Gemini output + verification section ---
{
  if [[ -s "$GEMINI_TMP" ]]; then
    cat "$GEMINI_TMP"
  else
    printf '# Fix Report: %s\n\n' "$TICKET_ID"
    printf '## Ticket Info\n'
    printf -- '- **Review Task:** %s\n' "$TICKET_REQUIRED_BY"
    printf -- '- **Affected Task:** %s — %s\n' "$TICKET_AFFECTED_TASK" "$TICKET_AFFECTED_TASK_TITLE"
    printf -- '- **Criterion:** %s\n' "$TICKET_CRITERION"
    printf -- '- **Files Declared:** %s\n\n' "$TICKET_FILES_INLINE"
    printf '## Files Changed\n(Gemini produced no output)\n\n'
    printf '## Patch Summary\n(Gemini produced no output)\n\n'
    printf '## Open Issues\nGemini exited with code %d and produced no output. See log: %s\n\n' \
      "$GEMINI_EXIT" "$LOG_FILE"
  fi
  printf '\n## Verification\n'
  printf '| Command | Output | Result |\n'
  printf '|---------|--------|--------|\n'
  printf '| `%s` | `%s` | %s |\n' \
    "$TICKET_VERIFICATION" "$VERIFY_OUTPUT_SHORT" "$VERIFY_RESULT"
} > "$REPORT_FILE"

echo "Fix report written  → $REPORT_FILE"

# --- Final exit ---
if [[ $GEMINI_EXIT -ne 0 ]]; then
  echo "ERROR: gemini exited with code $GEMINI_EXIT. See $LOG_FILE" >&2
  exit 1
fi

if [[ $VERIFY_EXIT -ne 0 ]]; then
  echo "VERIFICATION FAILED (exit $VERIFY_EXIT). Claude must inspect $REPORT_FILE before marking ticket done." >&2
  exit 1
fi

echo "Verification passed. Claude must update status.json to mark ticket '$TICKET_ID' done."
exit 0
