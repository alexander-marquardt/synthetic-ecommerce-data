#!/usr/bin/env python3
"""The test files that read no industrial type table: ``scripts/ci_type_free.json`` (#1035).

    ci_type_free.py --refresh TYPE_READS_JSON...   # add what green runs saw, drop what read

``scripts/ci_select.py`` does not select a listed file for a change only a type table's reader can
see. ``tests/type_reads.py`` writes what each run saw (the ``type-reads-*`` artifacts) and fails a
listed file that reads a table. A file that starts a process, or that asks the registry by name, is
never listed: the plugin cannot see into a process, nor past ``typespec.registered``'s cache.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TABLE = REPO / "scripts" / "ci_type_free.json"

#: A word in a test file, or in a ``tests/`` helper it imports, that keeps it off the list.
BLIND = re.compile(
    r"\b(subprocess|multiprocessing|ProcessPoolExecutor|popen|Popen|os\.system|pexpect|typespec)\b"
)
_HELPER = re.compile(r"^\s*(?:from|import)\s+([\w.]+)", re.MULTILINE)


def eligible(file: str, root: Path = REPO) -> bool:
    """Whether the recorder sees every read ``file`` can make."""
    seen: set[str] = set()
    stack = [file]
    while stack:
        path = stack.pop()
        if path in seen:
            continue
        seen.add(path)
        try:
            text = (root / path).read_text(encoding="utf-8")
        except OSError:
            if path == file:
                return False
            continue
        if BLIND.search(text):
            return False
        for name in _HELPER.findall(text):
            helper = "tests/" + name.split(".")[0] + ".py"
            if (root / helper).is_file():
                stack.append(helper)
    return True


def refreshed(old: list[str], runs: list[dict], root: Path = REPO) -> list[str]:
    """``old`` and what the runs ran, less what read a table or the recorder cannot follow."""
    read = {f for run in runs for f in run["read"]}
    ran = {f for run in runs for f in run["ran"]}
    return sorted(f for f in (set(old) | ran) - read if eligible(f, root))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--refresh", nargs="+", type=Path, required=True, metavar="JSON")
    args = parser.parse_args(argv)
    old = json.loads(TABLE.read_text(encoding="utf-8")) if TABLE.is_file() else []
    new = refreshed(old, [json.loads(p.read_text(encoding="utf-8")) for p in args.refresh])
    TABLE.write_text(json.dumps(new, indent=1) + "\n", encoding="utf-8")
    print(f"{TABLE.name}: {len(new)} files ({len(set(new) - set(old))} added, "
          f"{len(set(old) - set(new))} dropped)")  # fmt: skip
    return 0


if __name__ == "__main__":
    sys.exit(main())
