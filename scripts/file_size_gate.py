"""Refuse a file that grows past the line cap: elastic/prism's gate, on this tree.

    python3 scripts/file_size_gate.py                    # measure from origin/main
    python3 scripts/file_size_gate.py --base <rev> --pr-body-file <body.md>   # CI
    python3 scripts/file_size_gate.py --list             # every file over the cap
    python3 scripts/file_size_gate.py --warn-at-commit   # the pre-commit hook

A measured file over the cap in ``scripts/file_size_cap.txt`` may not hold more
lines than it held at the merge base, unless the pull-request body carries
``File-Size-Exception: `<path>` - <reason>`` (elastic/prism#11683). The rule,
the options and the messages are core's ``scripts/check_file_size.py``, which
``vendor/prism/`` holds byte for byte with its import closure
(``vendor/prism/PIN.txt``). This file sets the one thing that differs here:
:data:`SCOPE`, because this repository's layout is not core's. The rule and
how to resync the copy: ``docs/file-size-budget.md``.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VENDOR = REPO_ROOT / "vendor" / "prism"
PIN = VENDOR / "PIN.txt"

#: Where the gate measures, as git pathspecs: every tracked or untracked,
#: unignored file with one of core's measured suffixes (code and prose), except
#: the vendored core copy, which is core's to size. Core measures only its own
#: directories (``packages/*/src``, ``scripts/`` ...); here the largest files sit
#: at the root (``README.md``) and under ``src/``, ``tests/`` and ``prototypes/``.
SCOPE: tuple[str, ...] = (":(glob)**", ":(exclude)vendor/**")

sys.path.insert(0, str(VENDOR / "scripts"))
import check_file_size as core  # noqa: E402  (the vendored path is set up just above)

core.SCOPE = SCOPE
_core_merge_base = core.merge_base


def merge_base(root: Path, base: str) -> str:
    """The commit a change is measured from; a merge in progress is measured as it will be.

    A merge of main that stops before its commit (a conflict, ``--no-commit``) runs
    the pre-commit hook while ``HEAD`` is still the branch's old tip. Core's merge
    base of ``base`` and ``HEAD`` is then the commit the branch left, and every
    line main added since looks like the branch's growth (#398). The push gate
    judges the merge commit, whose merge base with ``base`` is the later of the two
    below, so the hook measures from it: the merge base of ``base`` and ``HEAD``,
    and that of ``base`` and ``MERGE_HEAD``. With no merge in progress this is core's.
    """
    left = _core_merge_base(root, base)
    try:
        merge_head = core._git(root, "rev-parse", "-q", "--verify", "MERGE_HEAD").strip()
        right = core._git(root, "merge-base", base, merge_head).strip()
        return core._git(root, "merge-base", "--independent", left, right).split()[0]
    except (core.CouldNotJudge, IndexError):
        return left


core.merge_base = merge_base


def pinned_files(pin: Path = PIN) -> dict[str, tuple[str, str]]:
    """``{path under vendor/prism: (mode, blob id)}``, as ``PIN.txt`` lists them."""
    files: dict[str, tuple[str, str]] = {}
    for line in pin.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or line.startswith("commit "):
            continue
        meta, path = line.split("\t", 1)
        mode, _kind, blob = meta.split()
        files[path] = (mode, blob)
    return files


def pinned_commit(pin: Path = PIN) -> str:
    """The core commit ``PIN.txt`` names."""
    for line in pin.read_text(encoding="utf-8").splitlines():
        if line.startswith("commit "):
            return line.split()[1]
    raise ValueError(f"{pin} names no core commit")


def main(argv: list[str] | None = None, *, root: Path | None = None, render=None) -> int:
    """Core's ``main``, on ``root`` (this repository by default)."""
    return core.main(argv, root=root if root is not None else REPO_ROOT, render=render)


if __name__ == "__main__":
    raise SystemExit(main())
