# Architecture

## Project Overview

A real estate search platform where users can browse, search, and save property listings. Admins manage inventory. The system is designed for incremental AI search capability without requiring a rewrite.

## Core Functional Scope

- User authentication and role-based access (buyer, agent, admin)
- Property listing browsing with pagination
- Structured search and filtering (location, price, type, size)
- Favorites / saved listings per user
- Admin CRUD for property inventory
- Future: AI-powered natural language search via RAG

## Non-Goals

- Payment processing or transaction management
- Mortgage calculators or financial tooling
- Real-time chat or messaging
- Map rendering (out of scope for initial phases)
- Mobile native apps

---

## System Boundaries

```
Browser (Next.js)
    │
    ▼
FastAPI (backend/)       ← all business logic, auth enforcement, data access
    │
    ├── Supabase (Postgres + Auth)
    │
    └── Search boundary  ← called by FastAPI only; never by the browser
            │
            ├── Phase 1–2: internal module at backend/app/services/search/
            ├── Phase 3+:  extracted to search-service/ (separate process)
            └── [Future]   Vector DB / RAG pipeline
```

- The browser **never** calls the search boundary directly.
- The browser **never** calls Supabase directly (no client-side Supabase queries for data).
- Supabase Auth tokens are validated by FastAPI on every request.
- The search boundary is stateless and called only by FastAPI.

---

## Frontend Responsibilities (Next.js)

- Render UI from API responses — no business logic
- Handle routing, loading states, and error display
- Manage auth session (Supabase Auth client, token storage)
- Pass user intent (search query, filters, form input) to FastAPI
- No direct database access
- No access control decisions (only hide UI; enforcement is backend)

## Backend Responsibilities (FastAPI)

- Own all business logic: validation, authorization, data transformation
- Enforce RBAC on every endpoint
- Orchestrate calls to Supabase (data) and search boundary (search)
- Return clean, typed response schemas to the frontend
- Own all write operations (create, update, delete)

## Search Boundary Responsibilities

- Accept structured or unstructured query input from FastAPI
- Return ranked property IDs or objects
- Remain stateless — no auth, no user context
- Initial implementation: internal module wrapping Postgres FTS or filter queries
- Extraction trigger: when search logic becomes complex enough to warrant isolation, or when AI search requires a separate runtime

---

## Search Boundary Evolution

The search boundary is a logical boundary from day one, but not necessarily a physical service.

| Phase | Implementation | Location |
|-------|---------------|----------|
| F0–F2 | Not yet needed | — |
| F3 | Internal module, Postgres FTS | `backend/app/services/search/` |
| F3+ | Extracted service if needed | `search-service/` |
| F7 | Vector search + RAG | `search-service/` (required) |

FastAPI's internal call interface to the search boundary does not change between phases. Only the implementation behind it evolves. Extraction to a separate process is a deployment decision, not an API change.

---

## Future AI Search / RAG Extension Path

1. **Phase 1 (F3):** Search module wraps Postgres FTS queries inside the backend
2. **Phase 2:** Add embedding generation on property ingest; store vectors in pgvector
3. **Phase 3:** Accept natural language queries; embed query; ANN search over vectors
4. **Phase 4 (F7):** RAG — retrieve top-k listings, pass to LLM for summarized response

The upgrade path requires no changes to FastAPI's external API or the frontend.
