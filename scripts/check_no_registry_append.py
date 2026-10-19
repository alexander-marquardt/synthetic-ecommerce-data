#!/usr/bin/env python3
"""Refuse a pull request that appends to a shared registry (gen#513). Stub: the table is empty."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import NamedTuple


class Registry(NamedTuple):
    path: str
    shapes: tuple[re.Pattern[str], ...]
    example: str
    form: str
    exists: tuple[str, ...]


REGISTRIES: tuple[Registry, ...] = ()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.parse_args(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
