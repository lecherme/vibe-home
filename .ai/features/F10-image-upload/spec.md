# F10 — Image Upload

**Status:** in_progress  
**Created:** 2026-06-03

## Goal

Replace hand-typed image URL inputs in the Admin property form with real file upload backed by Supabase Storage. Admins can upload images directly; the system stores them in the `vibe_home` bucket and writes the resulting public URLs into `properties.images`.

## Scope

### In scope
- Backend: `POST /api/v1/admin/uploads/property-image` endpoint (admin-gated, multipart/form-data)
- Frontend: upload button per image row in `property-form.tsx`; calls backend endpoint; fills URL field on success
- Supabase Storage bucket: `vibe_home` (already created, public)

### Out of scope
- Replacing existing picsum/external URLs in the database (handled separately)
- Image deletion from Storage on property delete (deferred)
- shadcn/ui or Zod refactor (separate feature)
- Drag-and-drop or multi-file batch upload

## Constraints

- Max 5 images per property (existing constraint retained)
- Allowed types: `image/jpeg`, `image/png`, `image/webp`
- Max file size: 5 MB
- Storage path: `properties/{uuid}.{ext}`
- URL inputs remain (fallback / existing data compatibility)
- No direct Supabase Storage access from frontend — upload goes through backend API
