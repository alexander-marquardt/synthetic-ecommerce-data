#!/usr/bin/env python3
"""Which pairs of feature heads conflict, and in which files (gen#513).

    git fetch origin 'refs/pull/*/head:refs/pr/*'
    python3 scripts/pair_conflicts.py refs/pr/761 refs/pr/762 refs/pr/763

Two PRs that each merge into main alone can still conflict with each other, so a check of one PR
against main does not see what the next merge meets. This runs ``git merge-tree --write-tree`` over
every pair of heads and counts the conflicting files per file: the census of gen#513, and the
measure of its target, 0 conflicts among PRs that each add a feature. A file
``scripts/merge_pr.sh`` rebuilds costs no builder anything, so it is counted apart.

Exit 0: no pair meets outside the rebuilt files. Exit 1: the pairs and the files, by hand first.
"""

from __future__ import annotations

import argparse
import collections
import itertools
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rebuilt_at_merge(root: Path) -> frozenset[str]:
    """The files ``scripts/merge_pr.sh`` resolves a conflict in by rebuilding them."""
    done = subprocess.run(
        [str(root / "scripts" / "merge_pr.sh"), "--print-generated"],
        capture_output=True,
        text=True,
        check=True,
    )
    return frozenset(done.stdout.split())


def conflicts(root: Path, left: str, right: str) -> list[str]:
    """The files that conflict when ``left`` and ``right`` merge; empty for a clean pair."""
    done = subprocess.run(
        ["git", "-C", str(root), "merge-tree", "--write-tree", "--name-only", "--no-messages"]
        + [left, right],
        capture_output=True,
        text=True,
    )
    # An unreadable head exits 1 too, as a conflict does, but writes no tree: that is no clean pair.
    if done.returncode not in (0, 1) or not done.stdout:
        raise SystemExit(f"pair_conflicts: {left} x {right}: {done.stderr.strip()}")
    return done.stdout.split("\n")[1:] if done.returncode == 1 else []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("heads", nargs="*", help="two or more refs, each a feature's head")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--generated", action="append", help="a file the merge rebuilds; default: merge_pr.sh's"
    )
    args = parser.parse_args(argv)
    if len(args.heads) < 2:
        raise SystemExit("pair_conflicts: name two heads or more: a pair is what it measures")
    rebuilt = frozenset(args.generated) if args.generated else rebuilt_at_merge(ROOT)
    by_hand: collections.Counter[str] = collections.Counter()
    at_merge: collections.Counter[str] = collections.Counter()
    pairs = hit = 0
    for left, right in itertools.combinations(args.heads, 2):
        pairs += 1
        files = [name for name in conflicts(args.root, left, right) if name]
        if not files:
            continue
        hit += 1
        print(f"{left} x {right}: {' '.join(files)}")
        by_hand.update(name for name in files if name not in rebuilt)
        at_merge.update(name for name in files if name in rebuilt)
    print(f"pairs={pairs} conflicting={hit}")
    for name, count in by_hand.most_common():
        print(f"{count} by hand {name}")
    for name, count in at_merge.most_common():
        print(f"{count} rebuilt {name}")
    return 1 if by_hand else 0


if __name__ == "__main__":
    raise SystemExit(main())
