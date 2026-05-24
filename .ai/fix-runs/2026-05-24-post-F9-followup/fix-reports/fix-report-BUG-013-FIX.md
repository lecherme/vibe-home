# Fix Report: BUG-013-FIX

## Ticket Info
- **Review Task:** open-bugs.md
- **Affected Task:** Configuration — BUG-013 — 生产环境 API URL 无 fallback，部署风险
- **Criterion:** BUG-013
- **Files Declared:** frontend/lib/api/config.ts, frontend/lib/api/properties.ts, frontend/lib/api/auth.ts, frontend/lib/api/favorites.ts, frontend/lib/api/admin.ts, frontend/lib/api/health.ts

## Files Changed
- frontend/lib/api/config.ts
- frontend/lib/api/properties.ts
- frontend/lib/api/auth.ts
- frontend/lib/api/favorites.ts
- frontend/lib/api/admin.ts
- frontend/lib/api/health.ts

## Patch Summary
Created `frontend/lib/api/config.ts` exporting `apiUrl` and throwing `NEXT_PUBLIC_API_URL is not configured` when the environment variable is absent. Replaced the inline `process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"` fallback in all five API modules with an import from the shared config.

## Open Issues
None

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec frontend npx tsc --noEmit` | 无输出 | **PASS — exit 0** |
| `grep -r "localhost:8000" frontend/lib/api/` | 无输出 | **PASS — 无残留** |
| `grep -r "NEXT_PUBLIC_API_URL" frontend/lib/api/` | 仅 config.ts 2 处（声明 + error message） | **PASS — 集中管理** |
