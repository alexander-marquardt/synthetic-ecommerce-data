#!/usr/bin/env python3
"""Which test files a pull request's change reaches (#495): the stub, every test file."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SMOKE: tuple[str, ...] = ()
FULL_RUN: tuple[str, ...] = ()
READS_WHOLE_TREE: tuple[str, ...] = ()
CONTENT_INSENSITIVE: dict[str, tuple[str, ...]] = {}


def tracked_files(root: Path) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        capture_output=True,
    ).stdout.decode()
    return sorted(p for p in out.split("\0") if p and (root / p).is_file())


class Tree:
    def __init__(self, root: Path = REPO) -> None:
        self.root = root
        self.files = tracked_files(root)
        self.py = [p for p in self.files if p.endswith(".py")]


def is_test_file(path: str) -> bool:
    name = Path(path).name
    return path.startswith("tests/") and name.startswith("test_") and name.endswith(".py")


def select(changed, tree=None, root: Path = REPO, modified=None):
    tree = tree or Tree(root)
    tests = sorted(p for p in tree.py if is_test_file(p))
    return tests, {t: "stub" for t in tests}


def selection_for_range(base: str, head: str, root: Path = REPO):
    return None


def main(argv: list[str] | None = None) -> int:
    print("\n".join(select([])[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
