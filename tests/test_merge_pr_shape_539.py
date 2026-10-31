"""``scripts/merge_pr.sh`` stays a short flow (#539).

The script reads as lock, fetch, merge main into a work tree, run CI on that tree, squash.
Its code lives in the files of ``scripts/merge_pr/`` that it sources, and its long
description in ``docs/merge-pr.md``. ``tests/test_merge_pr.py`` proves what it does.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "merge_pr.sh"
PARTS = REPO / "scripts" / "merge_pr"

#: The issue's Done-when line: the script is under this many lines.
MAX_LINES = 150

#: The tests that drive the script, which a change to any of its parts must select.
DRIVERS = (
    "tests/test_merge_pr.py",
    "tests/test_merge_pr_github_ci_348.py",
    "tests/test_merge_pr_local_ci_guard_366.py",
    "tests/test_merge_pr_red_log_453.py",
)


def test_the_merge_script_is_under_150_lines() -> None:
    lines = SCRIPT.read_text(encoding="utf-8").splitlines()
    assert len(lines) < MAX_LINES, f"scripts/merge_pr.sh is {len(lines)} lines"


def test_the_script_sources_every_part_and_only_real_ones() -> None:
    """A part the loop does not name never runs, and its functions die at the first call."""
    text = SCRIPT.read_text(encoding="utf-8")
    (names,) = re.findall(r"^for part in (.+); do$", text, flags=re.MULTILINE)
    assert sorted(names.split()) == sorted(p.stem for p in PARTS.glob("*.sh"))


def test_the_script_points_at_its_description() -> None:
    assert "docs/merge-pr.md" in SCRIPT.read_text(encoding="utf-8")
    assert (REPO / "docs" / "merge-pr.md").is_file()


@pytest.fixture(scope="module")
def ci_select():
    spec = importlib.util.spec_from_file_location(
        "ci_select_539", REPO / "scripts" / "ci_select.py"
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("part", ["config", "lock", "tree", "ci", "land"])
def test_a_change_to_a_part_selects_the_tests_that_drive_the_script(ci_select, part) -> None:
    """The selection keys on names in a test's text: ``merge_pr.sh`` alone misses a part."""
    path = f"scripts/merge_pr/{part}.sh"
    selected = ci_select.select([path], modified={path})[0]
    assert set(DRIVERS) <= set(selected)
