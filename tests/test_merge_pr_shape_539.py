"""``scripts/merge_pr.sh`` stays a short flow (#539).

The script reads as lock, fetch, merge main into a work tree, run CI on that tree, squash.
Its code lives in the files of ``scripts/merge_pr/`` that it sources, and its long
description in ``docs/merge-pr.md``. ``tests/test_merge_pr.py`` proves what it does.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "merge_pr.sh"

#: The issue's Done-when line: the script is under this many lines.
MAX_LINES = 150


def test_the_merge_script_is_under_150_lines() -> None:
    lines = SCRIPT.read_text(encoding="utf-8").splitlines()
    assert len(lines) < MAX_LINES, f"scripts/merge_pr.sh is {len(lines)} lines"
