# F30 — Ownership Map

| Task | Owner | Type |
|------|-------|------|
| T01 | codex | build |
| T02 | codex | build |
| T03 | codex | review |
| T04 | claude | acceptance |

## Codex constraints (T01, T02, T03)

- May only modify files listed in the task's Scope block in tasks.md
- T01 may additionally modify `backend/tests/test_eval_f27.py`, `backend/tests/test_f28_latency.py`, and `backend/tests/test_eval_f26.py` to update monkeypatch stubs and unpack patterns for changed function signatures
- Must not modify `status.json`, `frontend/**`, `backend/app/schemas/**`, `backend/app/api/**`
- Must not add new API endpoints, Pydantic schemas, or frontend components
- Must not run git commands
- Artifacts are captured by the wrapper; workers output to stdout only

## Claude constraints (T04)

- Reads `review.md` written by T03
- Writes `final-report.md` and updates `status.json`
- Does not modify any implementation files
- Does not run `run_task.sh` for acceptance
