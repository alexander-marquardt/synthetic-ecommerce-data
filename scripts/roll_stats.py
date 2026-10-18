#!/usr/bin/env python3
"""The release step that writes the rolled stats files (gen#373).

    uv run python scripts/roll_stats.py          # rewrite both files from this tree's build
    python3 scripts/roll_stats.py --list         # the files it rolls, one per line

``golden-retail/stats.json`` and ``golden-catalog/stats.json`` are build output. They
moved with every type or grocery PR, so every PR that committed them conflicted the rest
(16 of the 21 open PRs on 2026-10-18). A feature PR now commits neither:

* CI runs this script before the tests read the files (the ``tests`` job), so a PR's tests
  see the figures of the PR's own build and nothing is compared against a stale file;
* ``scripts/merge_pr.sh`` is the release step: it rebuilds both on the merged tree and
  commits them with a ``Rolled-By: scripts/merge_pr.sh`` trailer when the PR merges;
* ``scripts/check_no_stats_edit.py`` refuses a PR that edits either file without that
  trailer on its tip.

The roll is the two builders the repository already had, in this order: the retail
measurement (``prototypes/retail_drawings/retail_figures.py``, about 50 s) and the
catalog build (``ecom-generate build``, about 10 s, into a temporary directory, of which
only ``stats.json`` is kept: the other golden files are the PR's own to commit).
"""

from __future__ import annotations

import argparse
import contextlib
import io
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RETAIL = "golden-retail/stats.json"
CATALOG = "golden-catalog/stats.json"
#: The one list of the files a feature PR never commits.
ROLLED: tuple[str, ...] = (RETAIL, CATALOG)

Builder = Callable[[Path], None]


def build_retail(root: Path) -> None:
    """Rewrite ``golden-retail/stats.json`` (and the apparel decoy table beside it)."""
    script = root / "prototypes" / "retail_drawings" / "retail_figures.py"
    done = subprocess.run(
        [sys.executable, str(script)], cwd=root, capture_output=True, text=True
    )
    if done.returncode != 0:
        raise SystemExit(f"roll_stats: the retail measurement failed:\n{done.stdout}{done.stderr}")


def build_catalog(root: Path) -> None:
    """Rewrite ``golden-catalog/stats.json`` from a default build made in a temporary directory."""
    from unittest import mock

    from synthetic_ecommerce_data import generate_cli as cli

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "golden"
        # The build writes the field map into the source tree by default; a roll writes
        # no file but the stats (tests/test_catalog_golden.py sends it away the same way).
        with (
            mock.patch.object(cli, "field_map_target", lambda: Path(tmp) / "field_map.json"),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            code = cli.main(["build", "--out", str(out)])
        if code != 0:
            raise SystemExit("roll_stats: ecom-generate build refused the tree (see above)")
        target = root / CATALOG
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(out / "stats.json", target)


def roll(
    root: Path = ROOT, *, retail: Builder = build_retail, catalog: Builder = build_catalog
) -> list[str]:
    """Write every rolled file under ``root``; a builder that leaves one unwritten is refused."""
    for build in (retail, catalog):
        build(root)
    missing = [path for path in ROLLED if not (root / path).is_file()]
    if missing:
        raise SystemExit(f"roll_stats: the build wrote no {', '.join(missing)}")
    return list(ROLLED)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--list", action="store_true", help="print the rolled files and stop")
    args = parser.parse_args(argv)
    if args.list:
        print("\n".join(ROLLED))
        return 0
    for path in roll():
        print(f"rolled {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
