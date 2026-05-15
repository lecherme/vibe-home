# Claude Verification — T02

## Status
T02 代码已完成并验证。`codex-build-T02.md` artifact 不完整（见下方原因说明），本文件为补充记录。

## Files Changed

| 文件 | 变更类型 |
|------|---------|
| `frontend/lib/api/favorites.ts` | 新增 `FavoriteConflictError` 类 + `addFavorite` 409 分支 |
| `frontend/middleware.ts` | 未登录跳转时附加 `redirectTo` 参数 |

## Scope 符合性

- T02 scope 仅限上述两文件 ✓
- 未修改 `frontend/app/`、`frontend/components/` ✓
- 未修改 `status.json` ✓

## Diff 摘要

**`frontend/lib/api/favorites.ts`**
- 新增 `FavoriteConflictError extends Error`，已 export
- `addFavorite` 在 `res.status === 409` 时 `throw new FavoriteConflictError()`
- 非 409 错误仍 `throw new Error(...)`，行为不变

**`frontend/middleware.ts`**
- 未登录跳转逻辑增加一行：`redirectUrl.searchParams.set("redirectTo", \`${pathname}${request.nextUrl.search}\`)`
- 登录后回跳逻辑留给 T05（LoginForm）实现

## tsc --noEmit

Codex 在沙箱内执行了 `./node_modules/typescript/bin/tsc --noEmit`，结果：**PASS**。
（宿主机 `frontend/node_modules` 未安装，无法在宿主机复现；以 Codex 沙箱结果为准。）

## `codex-build-T02.md` 不完整原因

`run_codex.sh` 用 `tee "$REPORT_FILE"` 捕获 `codex exec` 的 stdout。本次运行中 Codex 的完整报告（含 diff）输出到了 stderr（进入 `.log` 文件），stdout 仅输出了空行，导致 artifact 只有 1 行。harness 输出路由问题，非代码逻辑问题。完整输出见 `codex-build-T02.log`（286KB，3616 行）。
