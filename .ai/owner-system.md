# Owner System

**Feature** is the collaboration unit. **Task** is the ownership unit.
Every task has exactly one owner. Collaboration happens through sequential tasks, never shared tasks.

---

## Owner Definitions

### Claude (Planning & Acceptance)
**Owns:**
- Architecture decisions and system boundary definitions
- Feature specs: goal, non-goals, acceptance criteria, dependencies
- Roadmap sequencing and priority
- Task decomposition and owner assignment for each feature
- Final acceptance review for every feature
- Escalation decisions
- `status.json` — Claude is the only owner that writes to this file

**Must NOT:**
- Write application code (frontend or backend)
- Make implementation decisions (file structure, library choices) without a spec
- Accept a feature without verifying all acceptance criteria
- Assign a task to more than one owner
- Write to `codex-build-report.md`, `gemini-build-report.md`, or `review.md`

---

### Codex (Backend & Critical Logic)
**Owns:**
- Project skeleton: folder structure, config files, boilerplate
- FastAPI routers, services, Pydantic schemas, ORM models
- Auth middleware and RBAC enforcement logic
- Search module implementation (internal or extracted)
- Database migrations
- Critical frontend logic: auth flow, API client layer (`lib/api/`)
- Code review of any logic-bearing code regardless of who wrote it

**Output artifact:** `codex-build-report.md` — written by Codex at the end of every build task.
**Review artifact:** `review.md` — written by Codex at the end of every review task.

**Must NOT:**
- Make product or architecture decisions
- Implement UI layout, styling, or component structure
- Modify shadcn primitives in `components/ui/`
- Skip writing tests for service-layer functions
- Write to `status.json` or `gemini-build-report.md`
- Begin a task before its declared dependency tasks are complete

---

### Gemini (UI & Low-Risk Implementation)
**Owns:**
- Page scaffolding and layout composition
- Feature components in `components/features/`
- CRUD views wired to existing API types
- Form handling (using existing validation schemas)
- Test drafting: frontend component tests, API integration test stubs
- Minor UI fixes and copy changes

**Output artifact:** `gemini-build-report.md` — written by Gemini at the end of every build task.

**Must NOT:**
- Implement business logic in components (no data transformation, no auth checks)
- Call Supabase directly from frontend code
- Modify `lib/api/` or `lib/auth/` (Codex owns these)
- Create new API endpoints or modify backend schemas
- Make routing or access control decisions
- Write to `status.json`, `codex-build-report.md`, or `review.md`
- Begin UI tasks before the relevant API types exist in `frontend/types/`

---

## Artifact Definitions

| File | Written by | Purpose |
|------|-----------|---------|
| `codex-build-report.md` | Codex | Summary of what was built, files changed, tests written, open issues |
| `gemini-build-report.md` | Gemini | Summary of what was scaffolded, components created, open issues |
| `review.md` | Codex | Code review findings: pass/fail per criterion, issues, required fixes |
| `final-report.md` | Claude | Acceptance summary: criteria met, criteria failed, disposition |
| `status.json` | Claude only | Canonical task list with statuses and activity log |

All artifacts live in `.ai/features/<feature>/`.

---

## Handoff Rules

Handoffs are artifact-based. A task is handed off when its output artifact is written and complete.

| From | To | Trigger | Required Artifact |
|------|----|---------|-------------------|
| Claude | Codex | Feature spec finalized | `spec.md` + `tasks.md` written in feature workspace |
| Codex | Claude | Build task complete | `codex-build-report.md` written |
| Codex | Gemini | API types published | `codex-build-report.md` confirms types in `frontend/types/` |
| Gemini | Claude | UI task complete | `gemini-build-report.md` written |
| Claude | Codex | Review requested | `acceptance.md` with criteria to verify |
| Codex | Claude | Review complete | `review.md` written |
| Claude | (done) | Feature accepted | `final-report.md` written; `status.json` updated |

Gemini must not start any UI task until the relevant `codex-build-report.md` confirms API types are published.

---

## Escalation Rules

Escalate to Claude when:
- A task requires a decision that changes system boundaries
- An implementation reveals a missing or conflicting spec
- Two owners disagree on where logic should live
- A dependency task is not complete and blocks progress

Escalate to Codex when:
- Gemini encounters logic that belongs in the service layer
- A frontend bug is caused by incorrect API behavior
- Auth or access control behavior is unclear

Do not resolve escalations by making assumptions. Block, write the blocker in the current artifact, and escalate.

---

## Enforcement Rule

If a worker modifies a restricted directory:
- It MUST be explicitly approved by Claude
- Otherwise review should FAIL

---

## Review and Acceptance Flow

```
Codex or Gemini writes output artifact
    │
    ▼
Claude reads artifact and checks against acceptance.md
    │
    ▼
Claude requests Codex review (writes review.md)
    │
    ▼
Claude makes final decision:
  - Pass → writes final-report.md, updates status.json to "done"
  - Fail → returns to owner with specific failure notes in final-report.md
            owner fixes and rewrites their artifact
            flow restarts from review step
```

Claude's acceptance is required before any feature is considered done. There is no self-acceptance.
Only Claude updates `status.json`.
