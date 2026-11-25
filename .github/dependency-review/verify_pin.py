"""Check, or renew, the pinned copy of core's dependency review (#1180).

elastic/prism is private and this public repository holds no secret that reads it, so CI
cannot check core out beside it as `../prism`. It runs a copy of the review's scripts instead,
under `.github/dependency-review/`, pinned by `PIN.json` beside this file: the core commit the
copy was taken from and each file's SHA-256. The layout keeps core's (`scripts/`,
`prism_engine/`), so the copy's own `from scripts import ...` resolves.

    python3 .github/dependency-review/verify_pin.py                    # check the copy
    python3 .github/dependency-review/verify_pin.py --update ../prism  # copy core's HEAD, re-pin

The check exits 1 and names a file that differs from its pin, is gone, or sits in a copied
directory without being pinned. `--update <core checkout> [--commit <rev>]` copies each file as
committed at that revision (never the checkout's uncommitted edits) and rewrites `PIN.json`.
Standard library only: it runs before anything is installed.
Docs: docs/internals/dependency-review.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIN = HERE / "PIN.json"
SOURCE = "elastic/prism"
#: Each copied file, here, and where it is in core.
FILES = {
    "scripts/dependency_review.py": "scripts/dependency_review.py",
    "scripts/dependency_review_images.py": "scripts/dependency_review_images.py",
    "scripts/docs_index_comment.py": "scripts/docs_index_comment.py",
    "scripts/bounded_process.py": "scripts/bounded_process.py",
    "prism_engine/strict_yaml.py": "packages/prism-engine/src/prism_engine/strict_yaml.py",
}
#: The directories whose every file must be pinned.
COPIED_DIRS = ("scripts", "prism_engine")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def problems(here: Path = HERE) -> list[str]:
    pin = json.loads((here / "PIN.json").read_text(encoding="utf-8"))
    found: list[str] = []
    for rel, want in sorted(pin["sha256"].items()):
        path = here / rel
        if not path.is_file():
            found.append(f"{rel}: gone")
        elif _sha(path.read_bytes()) != want:
            found.append(f"{rel}: differs from its pin")
    for directory in COPIED_DIRS:
        for path in sorted((here / directory).rglob("*")):
            if "__pycache__" in path.parts or not path.is_file():
                continue
            rel = path.relative_to(here).as_posix()
            if rel not in pin["sha256"]:
                found.append(f"{rel}: not in the pin")
    return found


def update(core: Path, commit: str, here: Path = HERE) -> str:
    """Copy FILES from ``core`` at ``commit`` and rewrite the pin; returns the full sha."""

    def git(*args: str) -> bytes:
        return subprocess.run(
            ["git", "-C", str(core), *args], check=True, capture_output=True
        ).stdout

    sha = git("rev-parse", f"{commit}^{{commit}}").decode().strip()
    hashes = {}
    for rel, upstream in FILES.items():
        data = git("show", f"{sha}:{upstream}")
        (here / rel).parent.mkdir(parents=True, exist_ok=True)
        (here / rel).write_bytes(data)
        hashes[rel] = _sha(data)
    pin = {"source": SOURCE, "commit": sha, "sha256": dict(sorted(hashes.items()))}
    (here / "PIN.json").write_text(json.dumps(pin, indent=2) + "\n", encoding="utf-8")
    return sha


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--update", type=Path, metavar="CORE", help="a checkout of elastic/prism")
    parser.add_argument("--commit", default="HEAD", help="the core revision to copy (--update)")
    args = parser.parse_args(argv)
    if args.update:
        sha = update(args.update, args.commit)
        print(f"copied {len(FILES)} files of {SOURCE} at {sha} and re-pinned them")
        return 0
    found = problems()
    for line in found:
        print(line)
    if found:
        print(
            "The copy of core's dependency review was edited by hand or only partly updated. "
            "Run `python3 .github/dependency-review/verify_pin.py --update <a core checkout>` "
            "and commit the result."
        )
        return 1
    print("dependency review copy: every pinned file matches its pin")
    return 0


if __name__ == "__main__":
    sys.exit(main())
