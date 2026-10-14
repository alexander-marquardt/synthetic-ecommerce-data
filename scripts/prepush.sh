#!/usr/bin/env bash
# The pre-push gate (elastic/prism#11677): see scripts/prepush.py and docs/pre-push-gate.md.
set -euo pipefail
exec python3 "$(cd "$(dirname -- "${BASH_SOURCE[0]:-.}")" && pwd -P)/prepush.py" "$@"
