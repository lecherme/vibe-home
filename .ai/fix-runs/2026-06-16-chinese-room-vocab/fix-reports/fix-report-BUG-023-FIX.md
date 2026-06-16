# Fix Report: BUG-023-FIX

## Ticket Info
- **Review Task:** open-bugs.md
- **Affected Task:** F16/F18 — BUG-023 — 中文数字房间词不解析为 bedrooms_min
- **Criterion:** BUG-023
- **Files Declared:** backend/app/services/ai_search/service.py

## Files Changed
- backend/app/services/ai_search/service.py

## Patch Summary
Added a bare-count bedroom extraction regex for `\d+房` inside `_normalize_query()`'s bedroom extraction block. The new pattern uses a negative lookahead to avoid matching non-bedroom terms such as `房源`, `房子`, `房价`, `房间`, `房龄`, and `房东`.

## Open Issues
None

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `bash tools/run_eval.sh` | ` Container vibe-home-backend-run-d63787010dde Creating ` | **PASS** |
