#!/usr/bin/env python3
"""Which test files one shard of the CI ``tests`` job runs (#348).

    ci_shards.py --shard K --of N     # the files of shard K (1..N), one per line
    ci_shards.py --shard all          # every test file, for a run that is not sharded
    ci_shards.py --refresh JUNIT...   # rewrite scripts/ci_shard_weights.json from junit reports

The workflow's ``tests`` job is a matrix of N shards on GitHub-hosted runners, each running
``pytest -n auto --dist loadgroup`` over the files this prints. The suite is about 27
minutes of work on one core and merges are serial, so how fast a merge lands is how fast
the slowest shard ends (``gen-merge-minutes``: docs/ci-sharding.md).

Every test file lands in exactly one shard, by construction: the files pytest collects
(``test_*.py`` and ``*_test.py`` under ``tests/``) are dealt out by the longest-first rule,
each to the shard with the least work so far, ties to the lower shard. A file's work is its
measured seconds in ``scripts/ci_shard_weights.json``; a file with no entry (a new one)
weighs ``DEFAULT_SECONDS``, so adding a test file never means editing the weights, and the
weights only go stale slowly. ``tests/test_ci_shards_348.py`` checks that every file is in
exactly one shard, that the workflow's matrix is the shard count, and that the shards stay
balanced by the weights.
"""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WEIGHTS = REPO / "scripts" / "ci_shard_weights.json"
#: Seconds of work assumed for a test file with no measured weight.
DEFAULT_SECONDS = 20.0
#: Files too heavy for one shard: listed in every shard, their test ids dealt out by
#: ``keeps`` (tests/ci_shard_split.py).
SPLIT_FILES: frozenset[str] = frozenset({"tests/test_merge_pr.py"})


def keeps(index: int, shard: int, count: int) -> bool:
    """Whether the split file's test at position ``index`` runs in shard ``shard`` (1..count)."""
    return index % count == shard - 1


def collected_test_files(root: Path = REPO) -> list[str]:
    """Every test file pytest collects, as repo-relative posix paths, sorted."""
    tests = root / "tests"
    found = {p for pattern in ("test_*.py", "*_test.py") for p in tests.rglob(pattern)}
    return sorted(p.relative_to(root).as_posix() for p in found)


def load_weights(path: Path = WEIGHTS) -> dict[str, float]:
    if not path.exists():
        return {}
    return {name: float(seconds) for name, seconds in json.loads(path.read_text()).items()}


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
    args = parser.parse_args(argv)
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
    print("\n".join(deal(collected_test_files(), args.of, load_weights())[number - 1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
