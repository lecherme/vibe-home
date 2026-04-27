# Codex Build Report

## Task Completed
- T03

## Files Changed
- `frontend/lib/api/properties.ts`

## API Types Published
- None

## Tests Written
- None

## Open Issues
- None
- Verified `frontend/lib/api/properties.ts` typechecks with `./node_modules/.bin/tsc --noEmit -p tsconfig.json`
- `PropertyApiError.message` now always includes the HTTP status code, including the no-session `401` path and non-2xx response path
