# F10 Image Upload — Tasks

---

## T01 — Codex: backend upload endpoint

- **owner:** codex
- **type:** build
- **depends_on:** none
- **allowed files:**
  - `backend/app/api/v1/admin/router.py`

**Requirements:**

1. Add imports: `uuid4` from `uuid`; `File`, `HTTPException`, `UploadFile` from `fastapi`; `get_supabase_client` from `app.core.supabase`
2. Define module-level constants:
   - `_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}`
   - `_CONTENT_TYPE_TO_EXT = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}`
   - `_MAX_FILE_SIZE = 5 * 1024 * 1024`
   - `_STORAGE_BUCKET = "vibe_home"`
3. New endpoint: `POST /uploads/property-image` (mounts as `/api/v1/admin/uploads/property-image`)
   - Param: `file: UploadFile = File(...)`
   - Auth: `current_user: UserRead = Depends(require_role("admin"))`; `del current_user`
   - Validate `file.content_type` in `_ALLOWED_CONTENT_TYPES`; raise HTTP 422 on failure
   - `data = await file.read()`; validate `len(data) <= _MAX_FILE_SIZE`; raise HTTP 413 on failure
   - `ext = _CONTENT_TYPE_TO_EXT[file.content_type]`
   - `path = f"properties/{uuid4()}.{ext}"`
   - `sb = get_supabase_client()`
   - `sb.storage.from_(_STORAGE_BUCKET).upload(path=path, file=data, file_options={"content-type": file.content_type})`
   - `url = sb.storage.from_(_STORAGE_BUCKET).get_public_url(path)`
   - Return `{"url": url}`
4. No other files modified
5. `python -c "from app.api.v1.admin.router import router"` exit 0

---

## T02 — Gemini: frontend upload UI

- **owner:** gemini
- **type:** build
- **depends_on:** T01
- **allowed files:**
  - `frontend/lib/api/admin.ts`
  - `frontend/components/features/admin/property-form.tsx`

**Requirements:**

### `frontend/lib/api/admin.ts`

1. Add `uploadPropertyImage(file: File): Promise<{ url: string }>` — does NOT use the existing `request()` helper (which adds `Content-Type: application/json`)
2. Build `FormData`, append `file` under key `"file"`
3. Get auth headers via `getAuthHeaders()` (Authorization only — no Content-Type override)
4. `fetch(buildUrl("/api/v1/admin/uploads/property-image"), { method: "POST", headers, body: formData })`
5. On non-ok response throw `AdminApiError` using existing `getErrorMessage(res)`
6. Return `res.json() as Promise<{ url: string }>`
7. Export `uploadPropertyImage` and add to `adminApi` object

### `frontend/components/features/admin/property-form.tsx`

1. Add `useRef` to React imports
2. Import `uploadPropertyImage` from `@/lib/api/admin`
3. Add state: `const [uploadingIndex, setUploadingIndex] = useState<number | null>(null)`
4. Add refs:
   - `const fileInputRef = useRef<HTMLInputElement>(null)`
   - `const pendingUploadIndexRef = useRef<number>(-1)`
5. Add `triggerUpload(index: number)`: sets `pendingUploadIndexRef.current = index`, then calls `fileInputRef.current?.click()`
6. Add `handleFileChange(e: React.ChangeEvent<HTMLInputElement>)`:
   - Get `file = e.target.files?.[0]` and `index = pendingUploadIndexRef.current`
   - Reset `e.target.value = ""`
   - If no file or index < 0, return
   - `setUploadingIndex(index)`
   - Try: `const { url } = await uploadPropertyImage(file)`; call `handleImageChange(index, url)`
   - Catch: `setFormError(err instanceof Error ? err.message : "Upload failed")`
   - Finally: `setUploadingIndex(null)`
7. Add hidden file input before the closing `</form>` tag:
   `<input ref={fileInputRef} type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={handleFileChange} />`
8. In each image row `<div className="flex gap-2">`, add Upload button after the URL input and before Remove:
   - Label: `uploadingIndex === index ? "Uploading..." : "Upload"`
   - `onClick={() => triggerUpload(index)}`
   - `disabled={isLoading || uploadingIndex !== null}`
   - Style: same pattern as existing buttons (e.g. `px-3 py-2 text-sm font-semibold ... rounded-md disabled:opacity-50`)
9. No other files modified; tsc pass

---

## T03 — Codex: review

- **owner:** codex
- **type:** review
- **depends_on:** T01, T02

Review against acceptance.md criteria.

---

## T04 — Claude: acceptance

- **owner:** claude
- **type:** acceptance
- **depends_on:** T03
