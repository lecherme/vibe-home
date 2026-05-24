# Closed Bug Registry

Resolved items moved from `open-bugs.md`.

Each entry should include fixed date, verification evidence, fixing commit/batch, and original source link.

---

### BUG-013 — 生产环境 API URL 无 fallback，部署风险

- **Fixed date:** 2026-05-24
- **Verification:** tsc exit 0；`grep -r "NEXT_PUBLIC_API_URL" frontend/lib/api/` 仅 config.ts 一处；`grep -r "localhost:8000" frontend/lib/api/` 无残留
- **Fixing batch:** `.ai/fix-runs/2026-05-24-post-F9-followup` — BUG-013-FIX
- **Fix:** 新建 `frontend/lib/api/config.ts` 统一导出 `apiUrl`，缺省时 throw `"NEXT_PUBLIC_API_URL is not configured"`；5 个 api 文件改为 import from config.ts
- **Original source:** [post-F9 smoke results § BUG-013](./../qa-runs/2026-05-18-post-F9-smoke/results.md)
- **Fix report:** [fix-report-BUG-013-FIX](./../fix-runs/2026-05-24-post-F9-followup/fix-reports/fix-report-BUG-013-FIX.md)
