"""Check that the vendored vulnerability gate still matches its pin (elastic/prism#16291).

Vendored from elastic/prism by `scripts/sister_vuln_gate.py write`; do not edit it here. Run
from `.github/vuln-gate/`: it reads `PIN.json` beside it and compares the SHA-256 of every
file the pin names. It exits 1 and names a file that differs, is gone or sits in a vendored
directory without being pinned. Standard library only.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GITHUB = HERE.parent
#: Directories (under vuln-gate/) whose every file must be pinned.
VENDORED_DIRS = (".github/scripts", "scripts")


def problems() -> list[str]:
    pin = json.loads((HERE / "PIN.json").read_text(encoding="utf-8"))
    found: list[str] = []
    for rel, want in sorted(pin["sha256"].items()):
        path = GITHUB / rel
        if not path.is_file():
            found.append(f"{rel}: gone")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != want:
            found.append(f"{rel}: differs from its pin")
    for directory in VENDORED_DIRS:
        for path in sorted((HERE / directory).rglob("*")):
            rel = path.relative_to(GITHUB).as_posix()
            if "__pycache__" in path.parts:
                continue
            if path.is_file() and rel not in pin["sha256"]:
                found.append(f"{rel}: not in the pin")
    return found


def main() -> int:
    found = problems()
    for line in found:
        print(line)
    if found:
        print(
            "The vendored vulnerability gate was edited by hand or only partly updated. "
            "Run `scripts/sister_vuln_gate.py write` from elastic/prism and commit the result."
        )
        return 1
    print("vulnerability gate: every pinned file matches its pin")
    return 0


if __name__ == "__main__":
    sys.exit(main())
