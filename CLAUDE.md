# CLAUDE.md

## Project overview

See `README.md` for:
- tech stack
- local setup
- API overview
- environment variables

## Start-of-session required reads

Before starting any work, read in order:

1. `.ai/orchestration.md`
2. `.ai/conventions.md`
3. `.ai/owner-system.md`

After identifying the current feature, read:

4. `.ai/features/<feature>/spec.md`
5. `.ai/features/<feature>/tasks.md`
6. `.ai/features/<feature>/status.json`

## Source of truth

- Do not use `.ai/roadmap.md` as the source of current project status — it reflects the original F0–F9 plan and is outdated.
- Current feature status is defined by `.ai/features/<feature>/status.json`.
- Accepted features are indicated by the presence of `final-report.md` under `.ai/features/<feature>/`.

## Execution rules

- Worker tasks must be run only through:
  `CODEX_MODEL=gpt-5.4 CODEX_BYPASS_SANDBOX=1 bash tools/run_task.sh <feature_dir> <task_id>`
- Claude acceptance tasks are executed directly, not through worker mode.
- Status guard commands must be run sequentially, never chained with `&&`.
- Resolve `needs_verification` with `verify-pass` or `verify-fail`, not `done`.

## Git rules

- Never use `git add -A`.
- Stage only files relevant to the current feature.
- Do not commit `direct_fixup` changes mid-review; commit only after the full feature passes.

## Safety rules

- Do not add unauthenticated debug/probe endpoints and push them to production.
- Prefer curl + JWT inside the container, or env-gated endpoints, for diagnostics.

## Language

- Respond only in Chinese or English.
