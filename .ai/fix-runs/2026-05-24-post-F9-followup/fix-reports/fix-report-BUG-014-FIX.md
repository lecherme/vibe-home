# Fix Report: BUG-014-FIX

## Ticket Info
- **Review Task:** open-bugs.md
- **Affected Task:** Auth — BUG-014 — 注册成功后未引导用户登录
- **Criterion:** BUG-014
- **Files Declared:** frontend/components/features/auth/RegisterForm.tsx

## Files Changed
- frontend/components/features/auth/RegisterForm.tsx

## Patch Summary
Added `useRouter` and a `useEffect` in `RegisterForm.tsx` that watches `isSuccess`, starts a 3-second timer after successful registration, redirects to `/login`, and clears the timer on cleanup. The existing success message and Back to Login link were kept unchanged.

## Open Issues
None.

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec frontend npx tsc --noEmit` | 无输出 | **PASS — exit 0** |
| 手动复测 BUG-014 | 3 秒自动跳 /login；Back to Login 立即跳转，均 PASS | **PASS — 2026-05-27** |
