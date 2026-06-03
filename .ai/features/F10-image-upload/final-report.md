# F10 Image Upload — Claude Acceptance Report (T04)

**Date:** 2026-06-03  
**Reviewer:** Claude (T04 acceptance owner)

## Disposition: ACCEPTED

---

## Feature Summary

F10 adds real file upload to the admin property form, backed by Supabase Storage. Execution followed the standard orchestration pipeline:

- **T01 (Codex):** Backend `POST /api/v1/admin/uploads/property-image` endpoint — admin-gated, multipart/form-data, MIME/size validation, Supabase Storage upload, public URL return. Required `python-multipart==0.0.20` dependency added.
- **T02 (Gemini → Claude fallback):** Gemini worker crashed (ECONNRESET + API invalid content). Claude applied frontend changes: `uploadPropertyImage()` in `frontend/lib/api/admin.ts` (FormData, no JSON helper), Upload button + hidden file input + in-flight state in `property-form.tsx`.
- **T03 (Codex review, 3 attempts):** First two attempts failed due to Codex CLI stdin block and wrong model (`gpt-5.3-codex`). Fixed `run_codex_review.sh` (`</dev/null`) and `CODEX_MODEL` propagation. Review found 2 blockers across 2 runs — both resolved via fix loop:
  - A9: submit button not disabled during upload → fixed (`disabled={isLoading || uploadingIndex !== null}`)
  - API types: `{ url: string }` inline → `PropertyImageUploadResponse` published to `frontend/types/admin.ts`
- **T04 (Claude):** This report.

---

## Criteria Results (from T03 review.md — final PASS run)

| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 — Backend endpoint, admin-gated | PASS | `require_role("admin")` on `POST /uploads/property-image` |
| A2 — Valid upload succeeds | PASS | Returns `{"url": ...}` from Supabase public URL |
| A3 — File type validation | PASS | HTTP 422 on unsupported MIME |
| A4 — File size validation | PASS | HTTP 413 on >5 MB |
| A5 — Storage path format | PASS | `properties/{uuid4()}.{ext}` |
| A6 — Upload button present | PASS | Per-row Upload button in property form |
| A7 — Upload fills URL field | PASS | `handleImageChange(index, url)` on success |
| A8 — Upload error shown | PASS | `setFormError(...)` on failure; URL field unchanged |
| A9 — Disabled during flight | PASS | All upload buttons + submit disabled while `uploadingIndex !== null` |
| A10 — URL input retained | PASS | Manual URL entry preserved |
| A11 — tsc passes | PASS | Verified: `docker compose exec frontend npx tsc --noEmit` exit 0 |
| A12 — Backend import check | PASS | Verified: `python -c "from app.api.v1.admin.router import router"` exit 0 |

---

## Open Items

- **WARNING (non-blocking):** No automated tests for the upload endpoint or frontend upload flow. MIME/size/error-path regressions are unguarded. Deferred — out of F10 scope.

---

## Pipeline Issues Recorded

| Issue | Root Cause | Fix Applied |
|-------|-----------|-------------|
| T02 Gemini worker failed | ECONNRESET + API invalid content after retries | Claude fallback |
| T03 Codex stdin block | `codex exec` reads stdin by default | Added `</dev/null` to `run_codex_review.sh` |
| T03 wrong model | `CODEX_MODEL` not propagated in review script | Added model flag to `run_codex_review.sh` |
| T03 empty review.md residue | Failed runs leave 0-byte artifact | Manual cleanup + `ALLOW_ARTIFACT_OVERWRITE=true` |

---

## Accepted
