# F30 — Tasks

## T01 — Relaxation optimization: embedding reuse + batch fetch + internal timing

**Owner:** codex
**Type:** build
**Depends on:** —

**Scope:**
- `backend/app/services/ai_search/service.py`
- `backend/app/core/logging.py`
- `backend/tests/test_eval_f27.py` — update monkeypatch stubs for `_resolve_result_ids` and `_apply_relaxation` to match new return signatures

**Done condition:**

The relaxation path in `ai_search()` no longer repeats embedding or semantic search:
- `embed_text(query)` is called at most once per `ai_search()` invocation for parsed
  property searches with non-empty query; the result is passed into
  `_resolve_result_ids()` and `_apply_relaxation()` rather than recomputed
- `_apply_relaxation()` receives the pre-computed semantic ranked IDs and applies
  relaxed filters against them, without calling `_resolve_result_ids()` internally
- Both the strict-filtering loop and the relaxed-filtering loop replace per-ID
  `get_by_id()` calls with a single batch fetch
- `logger.info("AI search timing", ...)` includes four new fields:
  `strict_filtering_ms`, `apply_relaxation_ms`, `relaxed_filtering_ms`,
  `relaxation_steps`
- `logging.py` whitelist includes those four new fields
- `docker compose exec -T backend python3 -c "import app.main; print('OK')"` passes

---

## T02 — Non-regression eval: F16 + F27

**Owner:** codex
**Type:** build
**Depends on:** T01

**Scope:** (no file modifications — eval only)

**Done condition:**
- `bash tools/run_eval.sh` exits 0 (F16 eval unchanged)
- `docker compose run --rm -v $(pwd)/backend/tests:/app/tests backend python3 -m pytest /app/tests/test_eval_f27.py -q` exits 0 with 28 passed

---

## T03 — Codex review

**Owner:** codex
**Type:** review
**Depends on:** T01, T02

---

## T04 — Claude acceptance

**Owner:** claude
**Type:** acceptance
**Depends on:** T03
