"""scripts/merge_pr.sh merges only a tree that is green after main is merged in (#54).

Each case builds a throwaway origin from this checkout's HEAD, pushes a PR
branch to it, and runs the script from a clone of that origin, with a stand-in
``gh`` on ``PATH`` that answers ``pr view`` and records ``pr merge``. The
checks are narrowed to one test (``MERGE_PR_CHECKS``): what is under test is
the script's order of operations, not the suite.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

_FAKE_GH = """#!/usr/bin/env bash
case "$1 $2" in
  "pr view") printf 'OPEN\\tfalse\\tpr-branch\\t%s\\tmain\\n' "$FAKE_GH_HEAD" ;;
  "pr merge") echo "$*" >>"$FAKE_GH_LOG" ;;
  *) echo "fake gh: unexpected $*" >&2; exit 2 ;;
esac
"""

pytestmark = pytest.mark.skipif(shutil.which("uv") is None, reason="the script runs uv")


_IDENTITY = {
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.invalid",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.invalid",
}


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, **_IDENTITY},
    ).stdout.strip()


@pytest.fixture
def world(tmp_path: Path) -> dict:
    env = {**os.environ, **_IDENTITY}
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
    # This checkout's HEAD as the origin's main; CI checks out full history so
    # the fetch never starts from a shallow repository.
    _git(origin, "fetch", "-q", str(REPO), "HEAD:refs/heads/main")
    _git(origin, "symbolic-ref", "HEAD", "refs/heads/main")
    checkout = tmp_path / "checkout"
    subprocess.run(["git", "clone", "-q", str(origin), str(checkout)], check=True)
    # The script under test is this tree's, not the HEAD commit's.
    shutil.copy2(REPO / "scripts" / "merge_pr.sh", checkout / "scripts" / "merge_pr.sh")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "gh").write_text(_FAKE_GH)
    (bin_dir / "gh").chmod(0o755)
    env.update(
        PATH=f"{bin_dir}{os.pathsep}{env['PATH']}",
        FAKE_GH_LOG=str(tmp_path / "gh.log"),
        TMPDIR=str(tmp_path),
    )
    return {"origin": origin, "checkout": checkout, "env": env, "log": tmp_path / "gh.log"}


def _open_pr(world: dict, plant: dict[str, str]) -> str:
    """A PR branch off main with ``plant``, then a later commit on main."""
    checkout = world["checkout"]
    _git(checkout, "switch", "-q", "-c", "pr-branch")
    for path, text in plant.items():
        (checkout / path).write_text(text)
    _git(checkout, "add", "-A", *plant)
    _git(checkout, "commit", "-q", "-m", "planted PR change")
    _git(checkout, "push", "-q", "origin", "pr-branch")
    head = _git(checkout, "rev-parse", "HEAD")
    _git(checkout, "switch", "-q", "main")
    (checkout / "README.md").write_text((checkout / "README.md").read_text() + "\nlater\n")
    _git(checkout, "commit", "-q", "-m", "main moves on after the PR's CI run", "README.md")
    _git(checkout, "push", "-q", "origin", "main")
    return head


def _run(world: dict, head: str, checks: str, *flags: str) -> subprocess.CompletedProcess:
    env = {**world["env"], "FAKE_GH_HEAD": head, "MERGE_PR_CHECKS": checks}
    return subprocess.run(
        [str(world["checkout"] / "scripts" / "merge_pr.sh"), *flags, "54"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_a_stale_golden_is_rebuilt_on_the_merged_tree_pushed_and_merged(world: dict) -> None:
    stats = world["checkout"] / "golden-catalog" / "stats.json"
    stale = stats.read_text().replace('"lines": ', '"lines": 1', 1)
    head = _open_pr(world, {"golden-catalog/stats.json": stale})
    result = _run(world, head, "tests/test_catalog_golden.py")
    assert result.returncode == 0, result.stdout + result.stderr
    pushed = _git(world["origin"], "rev-parse", "pr-branch")
    assert pushed != head, "the merged and rebuilt tree was not pushed"
    assert _git(world["origin"], "merge-base", "--is-ancestor", "main", pushed) == ""
    assert _git(world["origin"], "show", f"{pushed}:golden-catalog/stats.json") == _git(
        world["origin"], "show", "main:golden-catalog/stats.json"
    )
    merged = world["log"].read_text().split()
    assert merged[:3] == ["pr", "merge", "54"]
    assert merged[-3:] == ["--squash", "--match-head-commit", pushed]


def test_a_red_merged_tree_is_neither_pushed_nor_merged(world: dict) -> None:
    plant = {"tests/test_planted_red.py": "def test_planted():\n    assert False\n"}
    head = _open_pr(world, plant)
    result = _run(world, head, "tests/test_planted_red.py")
    assert result.returncode != 0
    assert "red on the merged tree; NOT pushed, NOT merged" in result.stderr
    assert _git(world["origin"], "rev-parse", "pr-branch") == head
    assert not world["log"].exists()


def test_a_dry_run_pushes_and_merges_nothing(world: dict) -> None:
    stats = world["checkout"] / "golden-catalog" / "stats.json"
    head = _open_pr(world, {"golden-catalog/stats.json": stats.read_text() + " "})
    result = _run(world, head, "tests/test_catalog_golden.py", "--dry-run")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "dry run: would push" in result.stdout
    assert _git(world["origin"], "rev-parse", "pr-branch") == head
    assert not world["log"].exists()
