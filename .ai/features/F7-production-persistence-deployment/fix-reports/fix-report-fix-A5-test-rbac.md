# Fix Report: fix-A5-test-rbac

## Ticket Info
- **Review Task:** T05
- **Affected Task:** T02 — Backend persistence rewrite
- **Criterion:** A5
- **Files Declared:** backend/tests/test_rbac_matrix.py

## Files Changed
- backend/tests/test_rbac_matrix.py

## Patch Summary
Removed the deleted `PROPERTIES` / `favorites_store` imports and all direct usages in `backend/tests/test_rbac_matrix.py`. Replaced them with local `_TEST_PROPERTIES` fixtures plus a `MagicMock` Supabase client contract, and patched the properties/admin/favorites service `get_supabase_client` call sites so the RBAC matrix test matches the updated persistence pattern used by the other A5-fixed tests.

## Open Issues
None.

## Verification
| Command | Output | Result |
|---------|--------|--------|
| `python3 -c "import sys, re; src=open('backend/tests/test_rbac_matrix.py').read(); sys.exit(0 if not re.search(r'from app\\.data\\.properties import.*\\bPROPERTIES\\b', src) and not re.search(r'\\bfavorites_store\\b', src) and not re.search(r'\\bPROPERTIES\\s*\\[', src) else 1)"` | `` | **PASS** |
