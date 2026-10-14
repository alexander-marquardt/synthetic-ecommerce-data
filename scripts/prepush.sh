#!/usr/bin/env bash
# The pre-push gate (elastic/prism#11677): see scripts/prepush.py and docs/pre-push-gate.md.
# It reads the CI workflows with pyyaml: the system python3 when it has it, else uv's.
set -euo pipefail
here="$(cd "$(dirname -- "${BASH_SOURCE[0]:-.}")" && pwd -P)"
if python3 -c 'import yaml' 2>/dev/null; then
  exec python3 "$here/prepush.py" "$@"
fi
exec uv run -q --locked python "$here/prepush.py" "$@"
