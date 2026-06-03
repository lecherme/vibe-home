# QA Run: 2026-06-03 Post-F10 Smoke

**Date:** 2026-06-03  
**Closed:** 2026-06-03  
**Run Status:** COMPLETED  
**Final Result:** 3 PASS / 0 FAIL  
**Tester:** Manual (user)  
**Branch/Commit:** `2f6c809` — feat(F10-image-upload): checkpoint at T04_done — ACCEPTED  
**Environment:** Production — frontend Vercel / backend JD Cloud Docker / Supabase Storage `vibe_home`  
**Scope:** Post-F10 smoke — upload endpoint reachable, upload button visible, end-to-end upload flow

---

## 结果记录

| ID | 描述 | Status | Notes |
|----|------|--------|-------|
| F10-S01 | 后端部署正常，`/api/v1/admin/uploads/property-image` 可达 | **PASS** | 用户确认后端部署无异常 |
| F10-S02 | Admin 属性表单中每行图片 URL 旁可见 Upload 按钮 | **PASS** | 用户确认前端入口可见 |
| F10-S03 | 选择图片文件后上传成功，URL 字段填入 Supabase Storage 公共 URL | **PASS** | 用户确认 "上传没问题了" |

---

## 未测项（非阻塞）

- 未触发 422（非图片文件类型）路径
- 未触发 413（>5MB 文件）路径
- 网络错误 fallback（A8）未手动验证

以上均属边界路径，核心 happy path 已通过生产环境验证。
