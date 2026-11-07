#!/usr/bin/env python3
"""Which test files one shard of the CI ``tests`` job runs (#348).

    ci_shards.py --shard K --of N     # the files of shard K (1..N), one per line
    ci_shards.py --shard all          # every test file, for a run that is not sharded
    ci_shards.py --shard K --of N --base B --head H   # the same, for the files B..H reaches (#495)
    ci_shards.py --plan K --of N --base B --head H    # ``shards=<n>`` then shard K's files
    ci_shards.py --refresh JUNIT...   # rewrite scripts/ci_shard_weights.json from junit reports
    ci_shards.py --workers FILE...    # the worker count for a shard running these files (#790)
    ci_shards.py --refresh-peaks PEAKS_JSON...   # rewrite scripts/ci_module_peaks.json

The workflow's ``tests`` job is a matrix of N shards on GitHub-hosted runners, each running
``pytest -n auto --dist loadgroup`` over the files this prints. The suite is about 27
minutes of work on one core and merges are serial, so how fast a merge lands is how fast
the slowest shard ends (``gen-merge-minutes``: docs/ci-sharding.md).

Every test file lands in exactly one shard, by construction: the files pytest collects
(``test_*.py`` and ``*_test.py`` under ``TEST_DIRS``, which is ``tests/``) are dealt out by the
longest-first rule,
each to the shard with the least work so far, ties to the lower shard. A file's work is its
measured seconds in ``scripts/ci_shard_weights.json``; a file with no entry (a new one)
weighs ``DEFAULT_SECONDS``, so adding a test file never means editing the weights, and the
weights only go stale slowly. ``tests/test_ci_shards_348.py`` checks that every file is in
exactly one shard, that the workflow's matrix is the shard count, and that the shards stay
balanced by the weights.

``--plan`` prints the files in run order (``run_order``): heaviest first, the files whose
tests xdist spreads last (``--dist loadgroup`` hands a free worker the next module in that
order, so an alphabetical list left a late-sorting heavy module as the tail of the run).
``--shard`` stays alphabetical.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WEIGHTS = REPO / "scripts" / "ci_shard_weights.json"
#: Seconds of work assumed for a test file with no measured weight.
DEFAULT_SECONDS = 20.0
#: Seconds of work (the weights') no planned shard may hold: a full run's shard is about 1121 s
#: and takes up to 0.99 s of wall clock per second of weight on a hosted runner, against the
#: job's ``timeout-minutes: 25`` (#704).
SHARD_BUDGET_SECONDS = 1200.0
#: Seconds of work (the weights') one shard of a change-scoped run takes on, the budget: a
#: smaller selection runs on fewer shards, so a pull request does not pay sixteen jobs' set-up
#: for a handful of files (#495), but never on a shard heavier than a full run's (#704).
SCOPED_SHARD_SECONDS = SHARD_BUDGET_SECONDS
#: Files too heavy for one shard: listed in every shard, their test ids dealt out by
#: ``keeps`` (tests/ci_shard_split.py).
SPLIT_FILES: frozenset[str] = frozenset(
    {"tests/test_merge_pr.py", "tests/test_merge_pr_github_ci_348.py"}
)


def keeps(index: int, shard: int, count: int) -> bool:
    """Whether the split file's test at position ``index`` runs in shard ``shard`` (1..count)."""
    return index % count == shard - 1


#: The directories pytest collects: ``testpaths`` of ``pyproject.toml``, which
#: ``tests/test_test_files_collected_362.py`` holds equal to this and to the tracked test files.
TEST_DIRS: tuple[str, ...] = ("tests",)


def collected_test_files(root: Path = REPO) -> list[str]:
    """Every test file pytest collects, as repo-relative posix paths, sorted."""
    found = {
        p
        for directory in TEST_DIRS
        for pattern in ("test_*.py", "*_test.py")
        for p in (root / directory).rglob(pattern)
    }
    return sorted(p.relative_to(root).as_posix() for p in found)


def load_weights(path: Path = WEIGHTS) -> dict[str, float]:
    if not path.exists():
        return {}
    return {name: float(seconds) for name, seconds in json.loads(path.read_text()).items()}


#: Each test module's peak resident memory on a CI worker, in MB (#790): ``--refresh-peaks``
#: writes it from the shards' ``module-peaks-*`` artifacts, and ``--workers`` reads it.
MODULE_PEAKS = REPO / "scripts" / "ci_module_peaks.json"
#: A module over this many MB is heavy: ``HEAVY_MB`` of ``tests/worker_peak.py``, the figure its
#: ``module peak memory:`` line names a module by.
HEAVY_MB = 1500
#: The workers of a shard with no heavy module: 3 x 1.5 GB fits a runner's 6 GB container (#790).
LIGHT_WORKERS = 3
#: The runner's cap on ``-n auto``: a self-hosted container sets it, a hosted runner does not.
WORKERS_ENV = "PYTEST_XDIST_AUTO_NUM_WORKERS"


def load_peaks(path: Path = MODULE_PEAKS) -> dict[str, int]:
    if not path.exists():
        return {}
    return {name: int(mb) for name, mb in json.loads(path.read_text(encoding="utf-8")).items()}


def workers(files: list[str], peaks: dict[str, int], cap: str | None) -> tuple[int | None, str]:
    """The worker count for a shard that runs ``files``, or None to keep the runner's, and why.

    A runner that caps ``-n auto`` below ``LIGHT_WORKERS`` (a 6 GB container's two) gets
    ``LIGHT_WORKERS`` when every file's recorded peak is at most ``HEAVY_MB``. A file with no
    recorded peak (a new module) counts as heavy. A runner with no cap, or a higher one, keeps it.
    """
    if not cap or not cap.isdigit() or int(cap) >= LIGHT_WORKERS:
        return None, f"workers: the runner's ({WORKERS_ENV}={cap or 'unset'})"
    heavy = [name for name in files if peaks.get(name, HEAVY_MB + 1) > HEAVY_MB]
    if heavy:
        named = ", ".join(
            f"{name} {peaks[name]} MB" if name in peaks else f"{name} not measured"
            for name in heavy
        )
        return None, f"workers: the runner's {cap}, over {HEAVY_MB} MB or not measured: {named}"
    return LIGHT_WORKERS, (
        f"workers: {LIGHT_WORKERS}, not the runner's {cap}: no module of this shard's plan "
        f"measured over {HEAVY_MB} MB ({MODULE_PEAKS.name})"
    )


def refresh_peaks(reports: list[Path]) -> dict[str, int]:
    """The peak table from the shards' module-peak files: each module's highest figure of its own.

    A file is one shard's ``{module: MB}``, which ``tests/worker_peak.py`` writes. A worker resets
    its high-water mark before each module but keeps what is resident, so a module that runs
    after a heavier one on the same worker can read over ``HEAVY_MB`` on that one's leftovers. A
    figure over ``HEAVY_MB`` and below its shard's highest is not counted. A figure at or under
    ``HEAVY_MB`` always is, since leftovers only add. A module with no counted figure is left
    out, and ``workers`` counts a module left out as heavy.
    """
    table: dict[str, int] = {}
    for report in reports:
        figures = {name: int(mb) for name, mb in json.loads(report.read_text("utf-8")).items()}
        top = max(figures.values(), default=0)
        for name, mb in figures.items():
            if mb <= HEAVY_MB or mb == top:
                table[name] = max(table.get(name, 0), mb)
    return dict(sorted(table.items()))


_SPREAD = re.compile(r"^XDIST_SPREAD\s*=\s*True\b", re.MULTILINE)


def spread_files(files: list[str], root: Path = REPO) -> frozenset[str]:
    """The files whose tests xdist spreads over the workers: a module that sets
    ``XDIST_SPREAD = True`` (tests/xdist_groups.py) and the ``SPLIT_FILES``."""
    spread = set(SPLIT_FILES & set(files))
    for name in files:
        try:
            text = (root / name).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if _SPREAD.search(text):
            spread.add(name)
    return frozenset(spread)


def run_order(
    files: list[str], weights: dict[str, float], spread: frozenset[str] | None = None
) -> list[str]:
    """The order pytest is given the files in: heaviest first, ties by name, spread files last.

    ``--dist loadgroup`` gives a free worker the next module in collection order, so a heavy
    module listed late starts when the others are nearly done and is the tail of the run.
    Longest-first closes the gap; a spread file is many small units, so it goes last as the
    filler that levels the workers' ends. Every file is listed once.
    """
    spread = SPLIT_FILES if spread is None else spread
    whole = [name for name in files if name not in spread]
    spreading = [name for name in files if name in spread]
    whole.sort(key=lambda name: (-weights.get(name, DEFAULT_SECONDS), name))
    return whole + sorted(spreading)


def deal(
    files: list[str],
    count: int,
    weights: dict[str, float],
    split: frozenset[str] | None = None,
) -> list[list[str]]:
    """Split ``files`` into ``count`` shards: heaviest file first, each to the lightest shard.

    A split file (``SPLIT_FILES``) is in every shard and weighs a ``count``-th of its seconds
    in each; with one shard it is just a file.
    """
    if count < 1:
        raise ValueError("a run needs at least one shard")
    split = SPLIT_FILES if split is None else split
    whole = [name for name in files if name not in split] if count > 1 else list(files)
    divided = [name for name in files if name in split] if count > 1 else []
    weight = {name: weights.get(name, DEFAULT_SECONDS) for name in files}
    shards: list[list[str]] = [list(divided) for _ in range(count)]
    load = [sum(weight[name] for name in divided) / count] * count
    for name in sorted(whole, key=lambda f: (-weight[f], f)):
        lightest = min(range(count), key=lambda i: (load[i], i))
        shards[lightest].append(name)
        load[lightest] += weight[name]
    return [sorted(shard) for shard in shards]


def scoped_files(base: str, head: str, root: Path = REPO) -> list[str] | None:
    """The test files the change ``base..head`` reaches (scripts/ci_select.py), or None for
    every test file: no range (a push to main, a manual run) or a diff git cannot read."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import ci_select

    chosen = ci_select.selection_for_range(base, head, root)
    return None if chosen is None else sorted(chosen)


def shards_needed(files: list[str], of: int, weights: dict[str, float]) -> int:
    """How many of the ``of`` shards a selection is dealt to: enough that none holds more than
    ``SCOPED_SHARD_SECONDS`` of work, at least one, at most ``of``.

    The average gives the first guess; the longest-first deal can leave one shard a file over
    it, so the count grows until the deal's own heaviest shard (a split file's share included)
    is within the budget (#704).
    """
    seconds = sum(weights.get(name, DEFAULT_SECONDS) for name in files)
    count = max(1, min(of, math.ceil(seconds / SCOPED_SHARD_SECONDS)))
    while count < of and max(_dealt_loads(files, count, weights)) > SCOPED_SHARD_SECONDS:
        count += 1
    return count


def _dealt_loads(files: list[str], count: int, weights: dict[str, float]) -> list[float]:
    """The seconds of work each of ``count`` shards holds when ``files`` are dealt to them."""
    return [
        sum(
            weights.get(name, DEFAULT_SECONDS) / (count if name in SPLIT_FILES and count > 1 else 1)
            for name in shard
        )
        for shard in deal(files, count, weights)
    ]


def plan(
    number: int, of: int, base: str = "", head: str = "", root: Path = REPO
) -> tuple[int, list[str]]:
    """``(shards, files)``: how many shards share the run, and shard ``number``'s files (none
    when the selection does not need that many shards)."""
    weights = load_weights()
    files = scoped_files(base, head, root) if base and head else None
    if files is None:
        return of, deal(collected_test_files(root), of, weights)[number - 1]
    active = shards_needed(files, of, weights)
    if number > active:
        return active, []
    return active, deal(files, active, weights)[number - 1]


def shard_loads(
    count: int,
    root: Path = REPO,
    weights: dict[str, float] | None = None,
    split: frozenset[str] | None = None,
) -> list[float]:
    """The seconds of work each shard holds by the weights."""
    weights = load_weights() if weights is None else weights
    split = SPLIT_FILES if split is None else split
    return [
        sum(
            weights.get(name, DEFAULT_SECONDS) / (count if name in split and count > 1 else 1)
            for name in shard
        )
        for shard in deal(collected_test_files(root), count, weights, split)
    ]


def refresh(reports: list[Path]) -> dict[str, float]:
    """Seconds per test file from junit reports: the sum of its tests' times."""
    seconds: dict[str, float] = defaultdict(float)
    for report in reports:
        for case in ET.parse(report).getroot().iter("testcase"):
            module = (case.get("classname") or "").split(".")
            # classname is ``tests.test_x`` or ``tests.test_x.TestClass``.
            for end in range(len(module), 0, -1):
                candidate = "/".join(module[:end]) + ".py"
                if (REPO / candidate).exists():
                    seconds[candidate] += float(case.get("time") or 0)
                    break
    return {name: round(total, 1) for name, total in sorted(seconds.items())}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--shard", help="1..N, or 'all' for every test file")
    parser.add_argument("--of", type=int, default=0, help="the number of shards (N)")
    parser.add_argument("--refresh", nargs="+", type=Path, metavar="JUNIT")
    parser.add_argument("--plan", help="shard K: print `shards=<n>`, then its files")
    parser.add_argument(
        "--base", default="", help="base of the change; with --head, scope the files"
    )
    parser.add_argument("--head", default="", help="head of the change")
    parser.add_argument(
        "--workers", nargs="+", metavar="FILE", help="print the worker count for these files"
    )
    parser.add_argument("--refresh-peaks", nargs="+", type=Path, metavar="PEAKS_JSON")
    parser.add_argument("--peaks", type=Path, default=MODULE_PEAKS, help="the module peak table")
    args = parser.parse_args(argv)
    if args.workers:
        count, why = workers(args.workers, load_peaks(args.peaks), os.environ.get(WORKERS_ENV))
        print(why, file=sys.stderr)
        if count is not None:
            print(count)
        return 0
    if args.refresh_peaks:
        table = refresh_peaks(args.refresh_peaks)
        args.peaks.write_text(json.dumps(table, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {args.peaks}")
        return 0
    if args.plan == "all":  # a local run: every test file, one shard
        every = collected_test_files()
        ordered = run_order(every, load_weights(), spread_files(every))
        print("\n".join(["shards=1", *ordered]))
        return 0
    if args.plan:
        if not args.plan.isdigit() or not 1 <= int(args.plan) <= max(args.of, 0):
            parser.error("give --plan K --of N with K in 1..N")
        shards, files = plan(int(args.plan), args.of, args.base, args.head)
        files = run_order(files, load_weights(), spread_files(files))
        print("\n".join([f"shards={shards}", *files]))
        return 0
    if args.refresh:
        WEIGHTS.write_text(json.dumps(refresh(args.refresh), indent=1) + "\n", encoding="utf-8")
        print(f"wrote {WEIGHTS}")
        return 0
    if args.shard == "all":
        print("\n".join(collected_test_files()))
        return 0
    if not args.shard or not args.shard.isdigit() or args.of < 1:
        parser.error("give --shard K --of N, or --shard all")
    number = int(args.shard)
    if not 1 <= number <= args.of:
        parser.error(f"shard {number} is not in 1..{args.of}")
    print("\n".join(plan(number, args.of, args.base, args.head)[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
