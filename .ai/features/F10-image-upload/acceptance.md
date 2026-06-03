# F10 Image Upload — Acceptance Criteria

## A1 — Backend endpoint exists and is admin-gated
`POST /api/v1/admin/uploads/property-image` returns 401/403 without valid admin token.

## A2 — Valid image upload succeeds
Upload a valid jpeg/png/webp file (≤5MB) as admin → HTTP 200 + `{ "url": "https://..." }`. URL is a valid public Supabase Storage URL under the `vibe_home` bucket.

## A3 — File type validation
Upload a non-image file (e.g. `.txt`, `.pdf`) → HTTP 422.

## A4 — File size validation
Upload a file >5MB → HTTP 413.

## A5 — Storage path format
Returned URL path matches `properties/{uuid}.{ext}` pattern.

## A6 — Frontend: Upload button present
Each image row in the admin property form has an "Upload" button.

## A7 — Frontend: Upload fills URL field
Click Upload, select a valid image → Upload button shows "Uploading..." while in flight → on success, the corresponding URL input is populated with the returned URL.

## A8 — Frontend: Upload error shown
If upload fails (network error, 4xx) → `formError` shows the error message; URL field unchanged.

## A9 — Frontend: Upload disabled during flight
While any upload is in progress, all Upload buttons and the form submit button are disabled.

## A10 — Frontend: URL input retained
Existing URL inputs still work; hand-typed URLs are not removed.

## A11 — tsc passes
`docker compose exec frontend npx tsc --noEmit` exit 0.

## A12 — Backend import check
`docker compose exec backend python -c "from app.api.v1.admin.router import router"` exit 0.
