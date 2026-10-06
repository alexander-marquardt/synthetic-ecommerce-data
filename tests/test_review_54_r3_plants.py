"""Round-3 review plants for #54: each asserts the SAFE behaviour.

A red case here is a finding; a green one is a property the review confirmed.
Reuses tests/test_merge_pr.py's throwaway-origin harness.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from test_merge_pr import REPO, _git, _open_pr, _run, world  # noqa: F401

# A gh that refuses the first merge (GitHub still recomputing mergeability,
# the case the retry loop exists for) and, meanwhile, another PR lands on main.
_GH_MAIN_MOVES = """#!/usr/bin/env bash
case "$1 $2" in
  "pr view") printf 'OPEN\\tfalse\\tpr-branch\\t%s\\tmain\\n' "$FAKE_GH_HEAD" ;;
  "pr merge")
    if [ ! -e "$FAKE_GH_LOG.first" ]; then
      touch "$FAKE_GH_LOG.first"
      o="$FAKE_ORIGIN"
      new=$(git -C "$o" commit-tree "main^{tree}" -p main -m "another PR lands")
      git -C "$o" update-ref refs/heads/main "$new"
      exit 1
    fi
    echo "$*" >>"$FAKE_GH_LOG" ;;
esac
"""


def test_q1_main_that_moves_during_the_merge_retries_is_not_merged_onto(world: dict) -> None:
    (world["checkout"].parent / "bin" / "gh").write_text(_GH_MAIN_MOVES)
    world["env"]["FAKE_ORIGIN"] = str(world["origin"])
    head = _open_pr(world, {"tests/test_planted_green.py": "def test_ok():\n    pass\n"})
    result = _run(world, head, "tests/test_planted_green.py")
    assert not world["log"].exists(), (
        "merged after main moved past the base the checks ran on:\n" + result.stdout
    )


def test_q1_a_pr_red_outside_checks_is_not_merged(world: dict) -> None:
    """The full suite (the PR's own CI) is red on the exact tree that merges."""
    plant = {"tests/test_planted_outside_checks.py": "def test_red():\n    assert False\n"}
    head = _open_pr(world, plant)
    result = _run(world, head, "")  # "" = the script's own default CHECKS
    assert result.returncode != 0 and not world["log"].exists(), (
        "merged a tree whose full suite is red:\n" + result.stdout[-800:]
    )


def test_q1_an_all_skipped_check_is_not_green(world: dict) -> None:
    plant = {
        "tests/test_planted_red.py": (
            "import pytest\npytestmark = pytest.mark.skip('flaky')\n"
            "def test_planted():\n    assert False\n"
        )
    }
    head = _open_pr(world, plant)
    result = _run(world, head, "tests/test_planted_red.py")
    assert not world["log"].exists(), "a check run with every test skipped merged:\n" + (
        result.stdout[-600:]
    )


def test_q1_the_rebuild_commit_touches_only_generated_files(world: dict) -> None:
    """uv run re-locks a stale uv.lock and git add -A commits it as 'Rebuild golden-catalog'."""
    pyproject = (world["checkout"] / "pyproject.toml").read_text()
    stale_lock = pyproject.replace('"numpy>=1.26",', '"numpy>=1.26",\n    "pyyaml>=6.0.3",', 1)
    head = _open_pr(world, {"pyproject.toml": stale_lock})
    result = _run(world, head, "tests/test_a_type_module_imported_first.py")
    assert result.returncode == 0, result.stdout + result.stderr
    pushed = _git(world["origin"], "rev-parse", "pr-branch")
    touched = _git(world["origin"], "show", "--name-only", "--format=", pushed).split()
    outside = [p for p in touched if not p.startswith("golden-catalog/")]
    assert not outside, f"the 'Rebuild golden-catalog' commit also carries {outside}"


def test_q2_a_conflict_the_rebuild_does_not_rewrite_is_not_taken_from_the_pr(
    world: dict,
) -> None:
    """GENERATED_RE covers all of golden-catalog/, the build writes only seven files."""
    checkout = world["checkout"]
    _git(checkout, "switch", "-q", "-c", "pr-branch")
    (checkout / "golden-catalog" / "NOTES.md").write_text("PR side\n")
    _git(checkout, "add", "golden-catalog/NOTES.md")
    _git(checkout, "commit", "-q", "-m", "PR notes")
    _git(checkout, "push", "-q", "origin", "pr-branch")
    head = _git(checkout, "rev-parse", "HEAD")
    _git(checkout, "switch", "-q", "main")
    (checkout / "golden-catalog" / "NOTES.md").write_text("main side: a real edit\n")
    _git(checkout, "add", "golden-catalog/NOTES.md")
    _git(checkout, "commit", "-q", "-m", "main notes")
    _git(checkout, "push", "-q", "origin", "main")
    result = _run(world, head, "tests/test_a_type_module_imported_first.py")
    assert not world["log"].exists(), (
        "a conflict on a file the build never writes was resolved silently for the PR:\n"
        + result.stdout
    )


_READ_DURING_REGISTRATION = """
import dataclasses, sys
from synthetic_industrial_products.catalog import breadth, typespec
row = dataclasses.replace(breadth.load_rows()[0], key="planted_rod", part_number_block=None)
spec = typespec.TypeSpec("planted_rod", breadth=row, module="x.planted_rod", part_number_block=1234)
seen = []
def discover(package=typespec.TYPES_PACKAGE):
    # A sibling type module that reads a block at import, as discover imports it.
    seen.append(typespec.block_of("planted_rod"))
    return {"planted_rod": spec}
typespec.discover = discover
seen.append(typespec.block_of("planted_rod"))
print(seen)
"""


def test_q3_block_of_does_not_answer_by_import_order() -> None:
    result = subprocess.run(
        [sys.executable, "-c", _READ_DURING_REGISTRATION],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr[-800:]
    first, after = eval(result.stdout)  # noqa: S307 - our own print of two ints
    assert first == after == 1234, f"block_of answered {first} during registration, {after} after"


def _job_command() -> str:
    ci = (REPO / ".github" / "workflows" / "ci.yaml").read_text()
    job = ci.split("  main-merged-tree:", 1)[1]
    return re.search(r"run: (uv run pytest .*)", job).group(1)


@pytest.mark.parametrize(
    "path, edit",
    [
        ("golden-catalog/stats.json", lambda t: t.replace('"lines": ', '"lines": 1', 1)),
        (
            "src/prism_synthetic_industrial/data/field_weights/synthetic_industrial_flat.yaml",
            lambda t: t + "\n# hand edit\n",
        ),
    ],
    ids=["stats-auto-merged-wrong", "field-weights-hand-edit"],
)
def test_q4_main_merged_tree_job_is_red_on_a_broken_main(tmp_path: Path, path: str, edit) -> None:
    tree = tmp_path / "main"
    subprocess.run(["git", "clone", "-q", str(REPO), str(tree)], check=True)
    shutil.copy2(REPO / ".github" / "workflows" / "ci.yaml", tree / ".github/workflows/ci.yaml")
    shutil.copy2(REPO / "scripts" / "merge_pr.sh", tree / "scripts" / "merge_pr.sh")
    target = tree / path
    target.write_text(edit(target.read_text()))
    result = subprocess.run(
        ["bash", "-c", _job_command()], cwd=tree, capture_output=True, text=True, check=False
    )
    assert result.returncode != 0, "main-merged-tree is green on a broken main"
