#!/usr/bin/env python3
"""Stub for the red commit: scans nothing and reports clean (#393)."""

from __future__ import annotations

import sys

SPECS: tuple[tuple[str, str], ...] = ()


def main(argv: list[str]) -> int:
    sys.stdout.write("customer-name-check: OK - 0 files, 0 commits, 0 texts scanned\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
