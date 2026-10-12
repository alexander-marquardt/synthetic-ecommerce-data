"""Refuse a file that grows past the line cap (elastic/prism#11683).

A stub: it judges nothing yet and passes every tree.
"""

from __future__ import annotations

from pathlib import Path


def main(argv: list[str] | None = None, *, root: Path | None = None, render=None) -> int:
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
