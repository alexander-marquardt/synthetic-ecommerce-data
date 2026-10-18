#!/usr/bin/env python3
"""Refuse a pull request that edits a rolled stats file by hand (gen#373).

    python3 scripts/check_no_stats_edit.py --base <sha> --head <sha>   # CI, the stats-roll job

``golden-retail/stats.json`` and ``golden-catalog/stats.json`` are rolled by
``scripts/merge_pr.sh`` when a PR merges, not committed by the PR (``scripts/roll_stats.py``
holds the list and the reason). A PR whose range ``base...head`` changes either file fails,
unless the tip commit carries the trailer ``Rolled-By: scripts/merge_pr.sh``, which only
``merge_pr.sh``'s rebuild commits write. The tip is what is read because the rebuild
regenerates the whole file: whatever an earlier commit put there is overwritten by it.

Exit 0: no rolled file is edited, or the release step wrote the tip. Exit 1: the files and
the commands that put them back.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from roll_stats import ROLLED  # noqa: E402

TRAILER_KEY = "Rolled-By"
TRAILER_VALUE = "scripts/merge_pr.sh"


def _git(root: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit(f"check_no_stats_edit: git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout


def edited(root: Path, base: str, head: str) -> list[str]:
    """The rolled files the range ``base...head`` changes."""
    names = _git(root, "diff", "--name-only", f"{base}...{head}", "--", *ROLLED).split()
    return [path for path in ROLLED if path in names]


def rolled_by_release_step(root: Path, head: str) -> bool:
    """Whether the tip commit's trailer block names the release step."""
    fmt = f"--format=%(trailers:key={TRAILER_KEY},valueonly)"
    values = _git(root, "log", "-1", fmt, head).split("\n")
    return any(value.strip() == TRAILER_VALUE for value in values)


def refusal(files: list[str], base: str) -> str:
    lines = [
        "stats-roll: this change edits files that are rolled when a PR merges, not by the PR:",
        *(f"  {path}" for path in files),
        "",
        "CI rewrites both from your build before the tests read them (scripts/roll_stats.py), and",
        "scripts/merge_pr.sh commits the rebuilt files with the PR, so a PR that commits them",
        "conflicts every other open PR. Put them back as they are on the base, in a new commit:",
        *(f"  git checkout {base} -- {path}" for path in files),
        "To see the figures of your build without committing them, run:",
        "  uv run python scripts/roll_stats.py",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    files = edited(args.root, args.base, args.head)
    if not files or rolled_by_release_step(args.root, args.head):
        return 0
    print(refusal(files, args.base))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
