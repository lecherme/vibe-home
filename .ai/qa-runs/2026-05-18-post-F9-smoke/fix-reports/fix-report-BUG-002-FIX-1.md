# Fix Report: BUG-002-FIX-1

## Ticket Info
- **Review Task:** QA-2026-05-18
- **Affected Task:** LoginForm — 登录无反应 — allowedDevOrigins fix attempt
- **Criterion:** BUG-002
- **Files Declared:** frontend/next.config.mjs

## Worker Execution Result

**Status: FAILED — ECONNRESET**

Gemini worker (`run_fix_gemini.sh`) encountered authentication error on startup:
```
Error authenticating: _GaxiosError: request to https://cloudcode-pa.googleapis.com/v1internal:loadCodeAssist failed, reason: read ECONNRESET
```

Despite the auth error, the worker produced a **partial patch** (Next.js config written with incorrect nesting):
- Placed `allowedDevOrigins` under `experimental.allowedDevOrigins`
- Correct location for Next.js 15+/16.x is top-level `allowedDevOrigins`
- Verification command failed (exit 127 — manual verification step not executable as shell command)

## Claude Fallback Correction

**Authorization:** Explicit user authorization — "授权 Claude fallback 修正 BUG-002-FIX-1 的 worker partial patch"

**Change:** Moved `allowedDevOrigins` from `experimental` nesting to top-level config.

## Files Changed
- `frontend/next.config.mjs`

## Final Patch (after Claude correction)
```diff
-const nextConfig = {};
+const nextConfig = {
+  allowedDevOrigins: [
+    "192.168.31.136",
+    "192.168.31.221",
+    "100.102.19.18",
+  ],
+};
```

## Scope Verification
| 项目 | 结果 |
|------|------|
| 修改文件 | frontend/next.config.mjs（仅此一个）|
| scope 合规 | ✓ |
| 地址正确 | ✓（三个 IP 齐全）|
| 配置层级 | ✓（顶层，非 experimental）|

## Verification
- **Container restart:** pending（需手动重启 frontend 后复测）
- **BUG-002 status:** 不标 fixed — pending manual verification
- **复测项目:** Console 无 blocked cross-origin 警告；Network 显示 Supabase auth 请求；登录后成功跳转
