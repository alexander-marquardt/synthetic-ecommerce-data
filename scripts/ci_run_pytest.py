#!/usr/bin/env python3
"""Run a CI shard's pytest command once (stub)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXIT_INFRA = 75


def worker_lost(text: str) -> bool:
    return False


def evidence(cgroup: Path = Path("/sys/fs/cgroup")) -> list[str]:
    return []


def main(argv: list[str]) -> int:
    command = argv[argv.index("--") + 1 :] if "--" in argv else argv
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
