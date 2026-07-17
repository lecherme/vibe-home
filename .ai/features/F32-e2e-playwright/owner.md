# F32 Owner Map

| Task | Owner  | Type       | Key constraint |
|------|--------|------------|----------------|
| T01  | codex  | build      | Only creates files under `e2e/` — no modifications to `frontend/` or `backend/` |
| T02  | codex  | build      | Only creates test files under `e2e/tests/` — no modifications to fixtures or config |
| T03  | codex  | build      | May modify any file under `e2e/` but must NOT add new test cases — stabilization only |
| T04  | codex  | review     | Reads all T01–T03 artifacts and `acceptance.md`; writes `review.md` |
| T05  | claude | acceptance | Claude performs final acceptance directly; writes `final-report.md` |
