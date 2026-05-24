# Fix Tickets — 2026-05-24 post-F9 followup

Standalone fix batch for bugs from the post-F9 QA run backlog.
Source: `.ai/bugs/open-bugs.md`

---

## BUG-013-FIX

- **Bug:** BUG-013 — 生产环境 API URL 无 fallback，部署风险
- **Owner:** Codex
- **Severity:** P2 / Medium
- **Allowed files:**
  1. `frontend/lib/api/config.ts` ← 新建
  2. `frontend/lib/api/properties.ts`
  3. `frontend/lib/api/auth.ts`
  4. `frontend/lib/api/favorites.ts`
  5. `frontend/lib/api/admin.ts`
  6. `frontend/lib/api/health.ts`
- **Requirements:**
  1. 新建 `frontend/lib/api/config.ts`，内容如下（不多不少）：
     ```ts
     const apiUrl = process.env.NEXT_PUBLIC_API_URL;
     if (!apiUrl) throw new Error("NEXT_PUBLIC_API_URL is not configured");
     export { apiUrl };
     ```
  2. `properties.ts`、`auth.ts`、`favorites.ts`、`admin.ts`：删除各自的 `const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"`，改为 `import { apiUrl } from "@/lib/api/config"`
  3. `health.ts`：删除函数内 inline 的 `const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"`，改为在文件顶部 `import { apiUrl } from "@/lib/api/config"`
  4. 5 个 api 文件不得保留任何 `localhost:8000` 字符串或独立 `NEXT_PUBLIC_API_URL` 读取
  5. error message 必须为：`NEXT_PUBLIC_API_URL is not configured`
  6. 不修改其他任何文件
  7. tsc 通过
- **Verification:** `docker compose exec frontend npx tsc --noEmit` exit 0
- **Status:** verified — tsc exit 0；无 localhost:8000 残留（2026-05-24）
