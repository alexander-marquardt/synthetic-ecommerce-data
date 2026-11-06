#!/usr/bin/env python3
"""Build the 100K files of ``tests/shared_builds.py`` once for a CI run (#790).

    uv run python scripts/build_shared_100k.py --out build/hundred_k

The ``hundred-k-builds`` job runs this and uploads ``--out``; each ``tests`` shard downloads the
directory and names it in ``SHARED_BUILDS_DIR``, where ``shared_builds.cached`` finds every file
under the name it would have written, and never builds. Two processes side by side: one 100K
build reduced to the price, measured and flat files, and the quiet-wheel build, whose patched
price model makes a catalog of its own. Anything already in ``--out`` goes first: a file left by
an earlier tree is never read.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests"))


def groups() -> list[str]:
    import shared_builds  # noqa: PLC0415  # tests/, put on the path above

    return ["one_build", *shared_builds.ON_THEIR_OWN]


def build_group(group: str, out: Path) -> list[Path]:
    import shared_builds  # noqa: PLC0415

    return shared_builds.prebuild(group, out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--group", help=argparse.SUPPRESS)  # one child's share of the work
    args = parser.parse_args(argv)
    if args.group:
        start = time.monotonic()
        for path in build_group(args.group, args.out):
            print(f"{path}: {path.stat().st_size // 1024} KB")
        print(f"{args.group}: {time.monotonic() - start:.0f} s")
        return 0
    shutil.rmtree(args.out, ignore_errors=True)
    args.out.mkdir(parents=True)
    children = [
        subprocess.Popen([sys.executable, __file__, "--out", str(args.out), "--group", group])
        for group in groups()
    ]
    failed = [child.args[-1] for child in children if child.wait() != 0]
    if failed:
        raise SystemExit(f"build_shared_100k: {', '.join(failed)} failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
