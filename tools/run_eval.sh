#!/usr/bin/env bash
# Run the F16 eval suite (backend/tests/test_eval.py) inside a one-off backend
# container. The runtime container image does not include the tests directory,
# so tests are mounted at /app/tests at run time.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TESTS_DIR="$REPO_ROOT/backend/tests"

docker compose run --rm \
  -v "$TESTS_DIR:/app/tests" \
  backend \
  python3 -m pytest /app/tests/test_eval.py -q "$@"
