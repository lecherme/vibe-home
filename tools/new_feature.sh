#!/usr/bin/env bash
# Create a new feature workspace with stable orchestration templates.
#
# Usage:
#   bash tools/new_feature.sh F3-search-filtering "Search & Filtering"

set -euo pipefail

FEATURE_SLUG="${1:-}"
FEATURE_TITLE="${2:-$FEATURE_SLUG}"

if [[ -z "$FEATURE_SLUG" ]]; then
  echo "Usage: $0 <feature-slug> [feature-title]" >&2
  exit 1
fi

cd "$(dirname "$0")/.."

FEATURE_DIR=".ai/features/$FEATURE_SLUG"

if [[ -e "$FEATURE_DIR" ]]; then
  echo "ERROR: feature workspace already exists: $FEATURE_DIR" >&2
  exit 1
fi

mkdir -p "$FEATURE_DIR"

cat > "$FEATURE_DIR/spec.md" <<EOF
# $FEATURE_TITLE

## Goal

TODO: Describe the user-facing outcome and the architectural purpose of this feature.

## Scope

TODO: List the backend, frontend, and shared deliverables.

## Non-Goals

TODO: List explicit exclusions so workers do not overbuild.

## Constraints

- All implementation must follow \`.ai/conventions.md\` and \`.ai/orchestration.md\`.
- Workers must implement only their assigned task.
- \`status.json\` is updated only by Claude Code orchestration.

## Dependencies

TODO: List prerequisite features and their required disposition.

## Required Env Vars

TODO: List new env vars, or write "No new env vars."
EOF

cat > "$FEATURE_DIR/tasks.md" <<EOF
# $FEATURE_TITLE — Tasks

Every task has exactly one owner. Collaboration happens through sequential tasks, not shared tasks.

---

## T01 — TODO task title

- **owner:** codex
- **type:** scaffold
- **depends_on:** none
- **title:** TODO task title

**Scope:**
- TODO: Define exactly what this task may create or modify.

**Done condition:** TODO

---

## T02 — Codex review

- **owner:** codex
- **type:** review
- **depends_on:** T01
- **title:** Review $FEATURE_SLUG implementation against acceptance criteria

**Scope:**
- Validate all implementation deliverables against \`acceptance.md\`.
- Check ownership boundaries and task artifacts.
- Write \`review.md\`.

**Done condition:** \`review.md\` written with a verdict, per-criterion results, and enough failure detail for Claude to choose task_retry, direct_fixup, or review_rerun.

---

## T03 — Claude acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T02
- **title:** Validate $FEATURE_SLUG and write final acceptance result

**Scope:**
- Read \`review.md\`.
- Write \`final-report.md\` with disposition \`accepted\` or \`failed\`.
- Update \`status.json\` feature status to \`done\` or \`failed\`.

**Done condition:** \`final-report.md\` written and \`status.json\` updated.
EOF

cat > "$FEATURE_DIR/owner.md" <<EOF
# $FEATURE_TITLE — Ownership Boundaries

This is a static ownership map. Runtime state comes from \`status.json\`.

## Codex

TODO: List Codex-owned files and boundaries.

## Gemini

TODO: List Gemini-owned files and boundaries, or write "No Gemini tasks in this feature."

## Claude

Claude owns planning, acceptance, and \`status.json\` updates.

## Boundary Rules

1. Workers must not modify \`status.json\`.
2. Workers must not create report artifacts directly; wrappers capture stdout.
3. Workers must not modify files outside the current task scope.
EOF

cat > "$FEATURE_DIR/acceptance.md" <<EOF
# $FEATURE_TITLE — Acceptance Criteria

T02 (Codex review) verifies every criterion below and writes \`review.md\`.
T03 (Claude acceptance) reads \`review.md\` and writes \`final-report.md\`.

---

## Criteria

| # | Criterion | Check |
|---|-----------|-------|
| A1 | TODO | TODO |

## Review and Acceptance

If review verdict is FAIL, Claude does NOT proceed directly to T03 acceptance.
Claude must:
1. Write \`last_review_failure\` to \`status.json\` with fix_path, failed_criteria, and fix_instructions.
2. Choose fix_path: task_retry, direct_fixup, or review_rerun.
3. Apply the fix and re-run review before acceptance.

## Rejection Conditions

- Any task modifies files outside its ownership boundary.
- Any worker modifies \`status.json\`.
- Any required artifact is missing or malformed.
EOF

cat > "$FEATURE_DIR/status.json" <<EOF
{
  "feature": "$FEATURE_SLUG",
  "status": "pending",
  "current_stage": "initialized",
  "current_owner": null,
  "next_step": "Fill spec.md, tasks.md, owner.md, acceptance.md, and task_manifest.json before starting T01",
  "last_review_failure": null,
  "tasks": [
    {
      "id": "T01",
      "title": "TODO task title",
      "owner": "codex",
      "type": "scaffold",
      "depends_on": [],
      "status": "pending",
      "retry_count": 0,
      "artifact": null
    },
    {
      "id": "T02",
      "title": "Review $FEATURE_SLUG implementation against acceptance criteria",
      "owner": "codex",
      "type": "review",
      "depends_on": ["T01"],
      "status": "pending",
      "retry_count": 0,
      "artifact": null
    },
    {
      "id": "T03",
      "title": "Validate $FEATURE_SLUG and write final acceptance result",
      "owner": "claude",
      "type": "acceptance",
      "depends_on": ["T02"],
      "status": "pending",
      "retry_count": 0,
      "artifact": null
    }
  ],
  "activity_log": [
    {
      "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
      "event": "feature workspace initialized from template",
      "by": "claude"
    }
  ]
}
EOF

cat > "$FEATURE_DIR/task_manifest.json" <<EOF
{
  "feature": "$FEATURE_SLUG",
  "tasks": {
    "T01": {
      "allowed_files": [
        "TODO/path/or/glob"
      ],
      "forbidden_files": [
        ".ai/**/status.json",
        ".env",
        ".env.*",
        "node_modules/**",
        "**/*.log"
      ],
      "expected_artifact": "codex-build-T01.md",
      "verify_commands": []
    },
    "T02": {
      "allowed_files": [],
      "forbidden_files": [
        ".ai/**/status.json"
      ],
      "expected_artifact": "review.md",
      "verify_commands": []
    }
  }
}
EOF

python3 tools/status_guard.py validate "$FEATURE_DIR"

echo "Created feature workspace: $FEATURE_DIR"
echo "Next: fill TODO sections, then run: bash tools/run_task.sh $FEATURE_DIR T01"
