"""Compare the pinned unit declaration with its source in the industrial deployment.

    uv run python scripts/check_industrial_unit_pin.py            # compare; exit 0 only on a match
    uv run python scripts/check_industrial_unit_pin.py --refresh  # rewrite the pin from the source

``tests/data/industrial_canonical_units.yaml`` is a verbatim copy of the
``canonical_units:`` block in elastic/prism-industrial-products, and the
contract test reads every unit's kind and exact size from it. The source is a
PRIVATE repository this repository's CI cannot read, so this comparison cannot
be a pytest: there it could only skip. It is run by hand, through an
authenticated ``gh``, whenever the deployment's ``canonical_units`` changes and
before a 100-type build.

It checks three things:

* the pin's recorded ``sha256`` is the digest of its own block (the same check
  ``tests/test_industrial_unit_pin.py`` runs everywhere);
* at the recorded ``commit`` the source file is the recorded ``blob`` and holds
  this block, so the pin names where it came from truthfully;
* on the source's default branch the block is still this one, byte for byte,
  comments included. A change elsewhere in the file is not drift.

Exit 0 on a match, 1 on a mismatch, and 2 when the source cannot be read. It
never passes a comparison it could not make.

``--refresh`` copies the block from the newest commit on the default branch that
touched the source file and rewrites the whole pin, digest included. The pin is
never edited by hand: the digest exists to make a hand edit red.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO = "elastic/prism-industrial-products"
SOURCE_PATH = "src/prism_industrial_products/data/customization.yaml"
PIN = Path(__file__).resolve().parents[1] / "tests" / "data" / "industrial_canonical_units.yaml"
KEY = "canonical_units:"

HEADER = """\
# PINNED COPY of the industrial deployment's `canonical_units:` block, verbatim.
#
# Written by `scripts/check_industrial_unit_pin.py --refresh`; never edit it by
# hand. `sha256` is the digest of everything from `canonical_units:` to the end
# of this file, and tests/test_industrial_unit_pin.py reds a block that no
# longer matches it. The script compares the block with its source.
#
# The contract test (tests/test_nested_entry_contract.py) reads each unit's kind
# and exact size from here, so a unit the deployment rules on -- `TPI` as a
# reciprocal length, elastic/prism#9877 -- cannot be redeclared in a test unseen.
"""


class SourceUnreadable(RuntimeError):
    pass


def digest(block: str) -> str:
    return hashlib.sha256(block.encode("utf-8")).hexdigest()


def split_pin(pin_text: str) -> tuple[dict, str]:
    """The pin's provenance mapping and its block (``canonical_units:`` to EOF)."""
    start = pin_text.index("\n" + KEY) + 1
    return (yaml.safe_load(pin_text[:start]) or {}).get("pin") or {}, pin_text[start:]


def block_of(source_text: str) -> str:
    """The ``canonical_units:`` block cut out of a customization file, verbatim.

    It runs to the first column-0 line after it, a comment included: a comment
    there introduces the next key. Trailing blank lines separate keys and are
    not the block's.
    """
    lines = source_text.splitlines(keepends=True)
    try:
        start = next(i for i, line in enumerate(lines) if line.rstrip("\n") == KEY)
    except StopIteration:
        raise SourceUnreadable(f"no top-level `{KEY}` in {REPO}/{SOURCE_PATH}") from None
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].strip() and not lines[i][0].isspace()),
        len(lines),
    )
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    return "".join(lines[start:end])


def render(commit: str, blob: str, block: str) -> str:
    provenance = (
        "pin:\n"
        f"  repo: {REPO}\n"
        f"  path: {SOURCE_PATH}\n"
        f"  commit: {commit}\n"
        f"  blob: {blob}\n"
        f"  sha256: {digest(block)}\n"
    )
    return HEADER + provenance + block


def hash_problems(pin_text: str) -> list[str]:
    provenance, block = split_pin(pin_text)
    recorded = provenance.get("sha256")
    if not recorded:
        return [f"{PIN.name} records no sha256: rewrite it with --refresh"]
    if recorded != digest(block):
        return [
            f"{PIN.name}'s block does not match its recorded sha256: it was edited by hand. "
            "Rewrite it with --refresh"
        ]
    return []


def compare(pin_text: str, *, source_at_pin: str, blob_at_pin: str, source_now: str) -> list[str]:
    """Every way the pin disagrees with its source; empty on a match."""
    provenance, block = split_pin(pin_text)
    problems = hash_problems(pin_text)
    if blob_at_pin != provenance.get("blob"):
        problems.append(
            f"at {provenance.get('commit')} the source is blob {blob_at_pin}, "
            f"not the recorded {provenance.get('blob')}"
        )
    taken = block_of(source_at_pin)
    if taken != block:
        problems.append(
            f"the block at the recorded commit {provenance.get('commit')} is not the pin's"
        )
    # measured against the recorded commit, so a hand-edited pin is not reported as drift
    if block_of(source_now) != taken:
        problems.append(
            f"{REPO}'s canonical_units has changed since the pin was taken: rewrite it with "
            "--refresh, then rebuild and rerun the suite"
        )
    return problems


def _gh(*args: str) -> str:
    if shutil.which("gh") is None:
        raise SourceUnreadable("gh is not on the PATH")
    done = subprocess.run(["gh", "api", *args], capture_output=True, text=True, timeout=60)
    if done.returncode != 0:
        raise SourceUnreadable(done.stderr.strip() or f"gh api exited {done.returncode}")
    return done.stdout


def fetch(ref: str) -> tuple[str, str]:
    """The source file's text and blob sha at ``ref``."""
    body = json.loads(_gh(f"repos/{REPO}/contents/{SOURCE_PATH}?ref={ref}"))
    return base64.b64decode(body["content"]).decode("utf-8"), body["sha"]


def newest_commit() -> str:
    """The newest commit on the default branch that touched the source file."""
    commits = json.loads(_gh(f"repos/{REPO}/commits?path={SOURCE_PATH}&per_page=1"))
    if not commits:
        raise SourceUnreadable(f"no commit touches {SOURCE_PATH}")
    return commits[0]["sha"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--refresh", action="store_true", help="rewrite the pin from the source")
    args = parser.parse_args(argv)
    try:
        if args.refresh:
            commit = newest_commit()
            text, blob = fetch(commit)
            PIN.write_text(render(commit, blob, block_of(text)), encoding="utf-8")
            print(f"REFRESHED {PIN.name} from {REPO}@{commit}")
            return 0
        pin_text = PIN.read_text(encoding="utf-8")
        provenance, _ = split_pin(pin_text)
        if not provenance.get("commit"):
            print(
                f"MISMATCH: {PIN.name} records no commit: rewrite it with --refresh",
                file=sys.stderr,
            )
            return 1
        source_at_pin, blob_at_pin = fetch(provenance.get("commit") or "")
        source_now, _ = fetch(newest_commit())
    except SourceUnreadable as error:
        print(
            f"FAILED: cannot read {REPO}/{SOURCE_PATH} ({error}). Nothing was compared. "
            "Authenticate gh with access to that repository and run again.",
            file=sys.stderr,
        )
        return 2
    problems = compare(
        pin_text, source_at_pin=source_at_pin, blob_at_pin=blob_at_pin, source_now=source_now
    )
    for problem in problems:
        print(f"MISMATCH: {problem}", file=sys.stderr)
    if problems:
        return 1
    print(f"MATCH: {PIN.name} is {REPO}'s canonical_units block at {provenance['commit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
