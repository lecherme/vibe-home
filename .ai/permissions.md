# Access Control Permission Matrix

This matrix documents the expected RBAC behavior from the F6 spec and the guard mechanism currently enforcing it in code.

Audited files:
- `backend/app/api/v1/auth/router.py`
- `backend/app/api/v1/properties/router.py`
- `backend/app/api/v1/favorites/router.py`
- `backend/app/core/security.py`
- `backend/app/api/v1/admin/router.py`

Legend:
- `get_current_user`: rejects missing or invalid bearer auth with `401`
- `require_non_admin_user`: wraps `get_current_user`, then rejects `admin` with `403`
- `require_role("admin")`: wraps `get_current_user`, then rejects non-admin users with `403`

| Router | Endpoint | Unauthenticated | User | Admin | Audit result |
| --- | --- | --- | --- | --- | --- |
| auth | `GET /api/v1/auth/me` | `401` via `get_current_user` | `200` via `get_current_user` | `200` via `get_current_user` | Matches spec |
| properties | `GET /api/v1/properties` | `401` via `get_current_user` | `200` via `get_current_user` | `200` via `get_current_user` | Matches spec |
| properties | `GET /api/v1/properties/search` | `401` via `get_current_user` | `200` via `get_current_user` | `200` via `get_current_user` | Matches spec |
| properties | `GET /api/v1/properties/{id}` | `401` via `get_current_user` | `200` via `get_current_user` | `200` via `get_current_user` | Matches spec |
| favorites | `POST /api/v1/favorites/{property_id}` | `401` via `get_current_user` inside `require_non_admin_user` | `201` via `require_non_admin_user` | `403` via `require_non_admin_user` | Matches spec |
| favorites | `DELETE /api/v1/favorites/{property_id}` | `401` via `get_current_user` inside `require_non_admin_user` | `204` via `require_non_admin_user` | `403` via `require_non_admin_user` | Matches spec |
| favorites | `GET /api/v1/favorites` | `401` via `get_current_user` inside `require_non_admin_user` | `200` via `require_non_admin_user` | `403` via `require_non_admin_user` | Matches spec |
| favorites | `GET /api/v1/favorites/{property_id}` | `401` via `get_current_user` inside `require_non_admin_user` | `200` via `require_non_admin_user` | `403` via `require_non_admin_user` | Matches spec |
| admin | `POST /api/v1/admin/properties` | `401` via `get_current_user` inside `require_role("admin")` | `403` via `require_role("admin")` | `201` via `require_role("admin")` | Matches spec |
| admin | `PUT /api/v1/admin/properties/{id}` | `401` via `get_current_user` inside `require_role("admin")` | `403` via `require_role("admin")` | `200` via `require_role("admin")` | Matches spec |
| admin | `DELETE /api/v1/admin/properties/{id}` | `401` via `get_current_user` inside `require_role("admin")` | `403` via `require_role("admin")` | `204` via `require_role("admin")` | Matches spec |

## RBAC Gaps

No RBAC gaps were identified in the scoped routers during this audit. The current endpoint guards match the expected role behavior defined for unauthenticated, `user`, and `admin` callers.
