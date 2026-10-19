#!/usr/bin/env python3
"""Refuse a tree that tracks a file the build writes (gen#536).

    python3 scripts/check_no_derived_files.py            # CI, the no-derived-files job

The retail totals, the sneak-peek samples and previews and the two generated docs are build
output. Committed, each moved with every retail PR, so each PR that committed one conflicted the
rest, and main went red whenever a merge did not roll them (gen#373 guarded the roll with 532
lines and none of the next 7 merges carried its trailer). They are built by
``scripts/build_derived.py``: CI builds them once per run and uploads them as the ``derived``
artifact, and a test reads a figure through ``retail_figures.figures()``, never a committed number.

Exit 0: no tracked path matches :data:`DERIVED`. Exit 1: the paths, and the command that builds
them without committing them.
"""

from __future__ import annotations

import argparse
import fnmatch
import subprocess
from pathlib import Path

#: The build's output paths, as globs over the repository-relative path (``*`` crosses a ``/``).
DERIVED: tuple[str, ...] = (
    "golden-retail/stats.json",
    "docs/figures.md",
    "docs/retail-apparel-decoys.md",
    "prototypes/retail_drawings/samples*.ndjson",
    "prototypes/retail_drawings/preview*.html",
)


def offenders(paths: list[str]) -> list[str]:
    """The ``paths`` that are build output."""
    return [p for p in paths if any(fnmatch.fnmatchcase(p, glob) for glob in DERIVED)]


def tracked(root: Path) -> list[str]:
    done = subprocess.run(
        ["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=False
    )
    if done.returncode != 0:
        raise SystemExit(f"check_no_derived_files: git ls-files failed: {done.stderr.strip()}")
    return [line for line in done.stdout.split("\n") if line]


def refusal(files: list[str]) -> str:
    return "\n".join(
        [
            "no-derived-files: this tree tracks build output, which CI builds as an artifact:",
            *(f"  {path}" for path in files),
            "",
            "Take them out of git (they stay on disk, ignored):",
            *(f"  git rm --cached {path}" for path in files),
            "To see the files your build writes, run:",
            "  uv run python scripts/build_derived.py --out build/derived",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    files = offenders(tracked(args.root))
    if not files:
        return 0
    print(refusal(files))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
