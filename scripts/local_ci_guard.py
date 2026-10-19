#!/usr/bin/env python3
"""Run one local CI command under a memory ceiling and a machine-wide lock (#366). STUB."""

from __future__ import annotations

import subprocess
import sys

WORKER_MB = 4500

#: Exit status of a command stopped for passing its ceiling.
EXIT_OVER_CEILING = 97
#: Exit status of a run that gave up waiting for the lock.
EXIT_LOCK_TIMEOUT = 98


def workers_for(argv: list[str], environ: dict[str, str]) -> int:
    return 0


def ceiling_mb(workers: int, environ: dict[str, str]) -> int:
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == "--":
        args = args[1:]
    return subprocess.run(args, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
