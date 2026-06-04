# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 — 依赖安装完整 | PASS | `frontend/package.json:12-28` includes `zod`, `react-hook-form`, `@hookform/resolvers`, `lucide-react`, and the required `@radix-ui/*` packages used by the generated shadcn components. |
| A2 — shadcn 基础组件存在 | PASS | Present under `frontend/components/ui/`: `button.tsx`, `input.tsx`, `textarea.tsx`, `select.tsx`, `dialog.tsx`, `table.tsx`, `toast.tsx`, `form.tsx`, `label.tsx`; also `toaster.tsx` and `frontend/hooks/use-toast.ts`. |
| A3 — property-form 使用 shadcn Form + react-hook-form | PASS | `frontend/components/features/admin/property-form.tsx:38-50` uses `useForm`, `:120-121` wraps with `<Form>` and `form.handleSubmit(...)`, and fields use `FormField`/`FormItem`/`FormControl`/`FormMessage`; handwritten `errors`/`validate()` state is gone. |
| A4 — Zod schema 覆盖所有字段 | FAIL | `frontend/lib/schemas/property.ts:4-7` uses `z.string().min(1)` for `title`, `description`, and `location`, which accepts whitespace-only input. The pre-migration form validated these fields with `.trim()`, so the new validation is weaker than the original behavior. |
| A5 — 上传功能不退化 | PASS | `uploadingIndex`, `fileInputRef`, `pendingUploadIndexRef`, `triggerUpload`, and `handleFileChange` are preserved at `frontend/components/features/admin/property-form.tsx:34-36` and `:79-102`; upload buttons disable during flight at `:295`, submit disables during upload at `:331`, and successful upload writes the returned URL into the correct image slot at `:92-96`. |
| A6 — 图片数组交互保留 | PASS | Add/remove/upload behavior remains intact at `frontend/components/features/admin/property-form.tsx:104-117` and `:263-310`; max-5 and min-1 guards are still enforced in the UI. |
| A7 — tsc 通过 | PASS | Re-ran `cd frontend && npx tsc --noEmit`: exit 0. |
| A8 — Admin 新增属性 happy path 通过 | FAIL | No manual or QA evidence for the create-property happy path is recorded in the feature artifacts or activity log. |
| A9 — Admin 编辑属性 happy path 通过 | FAIL | No manual or QA evidence for the edit-property happy path is recorded in the feature artifacts or activity log. |
| A10 — 其他页面未改动 | PASS | T01/T02 changed only `frontend/package*.json`, `frontend/components/ui/*`, `frontend/hooks/use-toast.ts`, `frontend/components/features/admin/property-form.tsx`, and authorized `frontend/lib/schemas/property.ts`; no `frontend/app/`, `frontend/lib/api/`, `frontend/lib/auth/`, `backend/`, or other feature-component changes were introduced by this feature. |
| Boundary — `status.json` ownership | PASS | The current `.ai/features/F11-shadcn-form-foundation/status.json` diff is the Claude-owned T03 state transition, and the activity log entries at `.ai/features/F11-shadcn-form-foundation/status.json:57-102` are authored by `"claude"`. No evidence shows Codex or Gemini editing `status.json`. |
| Boundary — API types published to `frontend/types/` | PASS | No API contract changes were introduced in T01/T02. Existing admin payload types remain in `frontend/types/admin.ts`, so there is no API type publication gap for this feature. |

## Issues Found
- BLOCKER: `frontend/lib/schemas/property.ts:4-7` weakens required-string validation. Whitespace-only `title`, `description`, and `location` now pass client validation, which regresses the original behavior.
- BLOCKER: A8 has no recorded happy-path verification for creating a property. The artifacts only show `tsc` and a smoke-level code inspection.
- BLOCKER: A9 has no recorded happy-path verification for editing a property. The artifacts only show `tsc` and a smoke-level code inspection.

## Required Fixes
- Update `frontend/lib/schemas/property.ts` so `title`, `description`, and `location` are trimmed before non-empty validation, preserving the original required-field behavior.
- Execute and record the admin create-property happy path required by A8.
- Execute and record the admin edit-property happy path required by A9.

## Approved Items
- shadcn/ui dependencies and base components were installed correctly, and the frontend type-check passes.
- `property-form.tsx` was migrated to `react-hook-form` + shadcn `Form` primitives, and the handwritten validation state was removed.
- The F10 upload path and image-array controls were preserved, including upload disabling and URL insertion behavior.
- No unauthorized source-file boundary violations were found in T01/T02.
- No evidence shows Codex or Gemini modifying `status.json`, and no API type publication gap was introduced.
