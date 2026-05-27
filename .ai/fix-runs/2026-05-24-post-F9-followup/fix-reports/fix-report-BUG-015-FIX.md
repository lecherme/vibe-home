# Fix Report: BUG-015-FIX

## Ticket Info
- **Review Task:** open-bugs.md
- **Affected Task:** Auth — BUG-015 — 密码复杂度校验缺失
- **Criterion:** BUG-015
- **Files Declared:** frontend/lib/auth/password-validation.ts, frontend/components/features/auth/ResetPasswordForm.tsx, frontend/components/features/auth/RegisterForm.tsx

## Files Changed
- frontend/lib/auth/password-validation.ts
- frontend/components/features/auth/ResetPasswordForm.tsx
- frontend/components/features/auth/RegisterForm.tsx

## Patch Summary
Added `validatePassword(password): string | null` with length, lowercase, uppercase, and digit checks. Replaced the reset form’s length-only check with `validatePassword`, and added the same validation in the register form before the confirm-password check.

## Open Issues
None

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `docker compose exec frontend npx tsc --noEmit` | 无输出 | **PASS — exit 0** |
| 手动复测 RegisterForm | `pass` → 长度错误；`password1` → 缺大写；`PASSWORD1` → 缺小写；`Password` → 缺数字；`Password1/Password2` → 密码不匹配（复杂度通过才到此步）；`Password1/Password1` → 通过前端校验，触发 Supabase 注册，被 email rate limit 拦截（属基础设施限制，非代码问题）| **PASS — 2026-05-27** |
| 手动复测 ResetPasswordForm | code verified only；已接入 `validatePassword`，但因 Supabase email rate limit 无法获取新 recovery link，未完成真实表单手动复测；等限流恢复后补测 reset 表单 | **pending — 待补测** |
