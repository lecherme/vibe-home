# F0 — Owner Map

This is a static ownership map. Runtime state (which task is active, what has completed) comes from `status.json`.

---

## Task Ownership

| Task | Owner | Rationale |
|------|-------|-----------|
| T01 | Codex | Backend skeleton, FastAPI structure, config loading — critical logic |
| T02 | Codex | Frontend skeleton, Next.js setup, folder structure — critical foundation |
| T03 | Gemini | Health status page — presentational UI, no business logic |
| T04 | Codex | Documentation — technical setup instructions |
| T05 | Codex | Review — validates all implementation against acceptance criteria |

---

## Owner Constraints

### Codex (T01, T02, T04, T05)
- Owns backend skeleton, frontend skeleton, and documentation
- Must create folder structure that matches `.ai/conventions.md`
- Must not implement UI layout or styling (T03 is Gemini's)
- Must write `codex-build-report.md` after T01, T02, T04
- Must write `review.md` after T05

### Gemini (T03)
- Owns health status page UI only
- Must not modify backend code
- Must not modify `lib/api/` or `lib/auth/` (empty in F0, but Codex-owned)
- Must use `NEXT_PUBLIC_API_URL` from env; no hardcoded URLs
- Must write `gemini-build-report.md` after T03

---

## Collaboration Rules

- T02 depends on T01 — Gemini cannot start T03 until Codex completes T02
- T05 depends on T01–T04 — Codex review runs only after all implementation tasks are done
- No shared tasks — every task has exactly one owner
- Handoffs happen through artifacts: Codex writes `codex-build-report.md`, Gemini reads it to understand what's available
