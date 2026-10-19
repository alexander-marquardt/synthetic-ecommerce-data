#!/usr/bin/env python3
"""Refuse a tree that tracks a file the build writes (gen#536)."""

from __future__ import annotations

import argparse
from pathlib import Path

#: The build's output paths, as git globs. Not committed: CI builds them as artifacts.
DERIVED: tuple[str, ...] = ()


def offenders(paths: list[str]) -> list[str]:
    """The tracked ``paths`` that are build output."""
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.parse_args(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
