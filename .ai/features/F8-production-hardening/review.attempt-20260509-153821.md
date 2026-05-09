# Review

## Verdict
FAIL

## Criteria Results
| Criterion | Result | Notes |
|-----------|--------|-------|
| A1 | PASS | `backend/app/main.py:21-40` uses explicit `allow_origins`, `allow_methods`, and `allow_headers` lists with no `*`. `backend/.env.example:7` documents `CORS_ALLOWED_ORIGINS`. A local preflight probe against a disallowed method returned `400 Disallowed CORS method`. |
| A2 | FAIL | `backend/.venv/bin/python -m pytest backend/tests/test_rate_limiting.py -q` passed, and `backend/.env.example:8` documents `RATE_LIMIT_AUTH`. However the implementation achieves this by adding a new `POST /api/v1/auth/me` endpoint in `backend/app/api/v1/auth/router.py:114-119` and rate-limiting that synthetic route. The app’s real auth flows still bypass this router via Supabase client calls in `frontend/lib/auth/session.ts:5-14`, so production auth traffic is not actually hardened. |
| A3 | PASS | `backend/app/core/logging.py:11-50` configures JSON-line logging with `level`, `timestamp`, `message`, and `request_id`. `backend/app/main.py:44-60` injects a UUID request id per request. A local probe confirmed valid JSON output and a non-null `request_id` for a log emitted inside request handling. |
| A4 | PASS | `backend/app/services/admin/service.py:78-86` deletes matching `favorites` rows before deleting the property. `backend/.venv/bin/python -m pytest backend/tests/test_admin_properties.py -q` passed (`18 passed`), and `backend/tests/test_admin_properties.py:243-251` plus `:314-328` assert the deleted property is removed from both properties and favorites state. `backend/app/services/favorites/service.py:68-93` derives favorites lists from the `favorites` table, so removing those rows removes the property from user favorites lists. |

## Issues Found
- BLOCKER: `backend/app/api/v1/auth/router.py:114-119` adds a new `POST /api/v1/auth/me` endpoint solely to satisfy rate-limit testing. This is a new API surface, not part of the feature spec, and it does not protect the app’s real sign-in/sign-up traffic, which still goes through Supabase in `frontend/lib/auth/session.ts:5-14`.
- WARNING: `backend/requirements.txt:2` adds `slowapi`, but the runtime uses a custom in-memory `AuthRateLimiter` instead. The dependency is currently dead weight and may mislead maintainers about the actual rate-limiting mechanism.

## Required Fixes
- Remove the synthetic `POST /api/v1/auth/me` endpoint.
- Apply rate limiting only to real backend auth mutation endpoints. If this codebase has no such backend endpoints, treat that as a blocker against T02 instead of inventing a new route, and reconcile the task/spec with the actual auth architecture.
- Keep the passing rate-limit test evidence, but rewrite the test to exercise the real protected auth endpoint(s) once those exist.

## Approved Items
- CORS hardening is correctly implemented and verified at runtime for a disallowed preflight method.
- Structured JSON logging is wired at app startup, and request-scoped logs include a UUID `request_id`.
- Property deletion correctly cascades to `favorites`, and the updated admin-property tests pass.
- No frontend components were changed, so no frontend business-logic violation was introduced by this feature.
- `status.json` shows only Claude-owned activity entries; I found no evidence of Codex or Gemini modifying it.
- No new backend schema types were introduced by this feature; existing auth types are already published in `frontend/types/auth.ts`.
