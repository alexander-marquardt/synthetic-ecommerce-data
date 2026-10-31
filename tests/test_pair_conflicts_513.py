"""The issue's pairwise check: two feature heads branched from one main merge clean (gen#513).

``scripts/pair_conflicts.py`` runs ``git merge-tree --write-tree`` over every pair of the heads it
is given. These tests build the pairs in a throwaway repository: two features in new files, two
features appending to one file, and two that meet in a file the merge rebuilds.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import pair_conflicts  # noqa: E402

GENERATED = "golden-catalog/stats.json"
REGISTRY = "docs/registry.md"


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
         "-c", "commit.gpgsign=false", *args],
        capture_output=True,
        text=True,
    )  # fmt: skip
    assert done.returncode == 0, f"git {args}: {done.stderr}"
    return done.stdout.strip()


def _branch(repo: Path, name: str, files: dict[str, str]) -> None:
    _git(repo, "switch", "-q", "-c", name, "main")
    for path, text in files.items():
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", name)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    (root / "docs").mkdir()
    (root / "golden-catalog").mkdir()
    (root / REGISTRY).write_text("one\n", encoding="utf-8")
    (root / GENERATED).write_text("{}\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    return root


def _run(repo: Path, capsys, *heads: str) -> tuple[int, str]:
    argv = ["--root", str(repo), "--generated", GENERATED, *heads]
    code = pair_conflicts.main(argv)
    return code, capsys.readouterr().out


def test_two_features_in_new_files_merge_clean(repo: Path, capsys) -> None:
    _branch(repo, "a", {"docs/feature-a.md": "a\n"})
    _branch(repo, "b", {"docs/feature-b.md": "b\n"})
    code, out = _run(repo, capsys, "a", "b")
    assert code == 0, out
    assert "pairs=1 conflicting=0" in out


def test_two_appends_to_one_file_conflict_and_the_file_is_named(repo: Path, capsys) -> None:
    _branch(repo, "a", {REGISTRY: "one\na\n"})
    _branch(repo, "b", {REGISTRY: "one\nb\n"})
    code, out = _run(repo, capsys, "a", "b")
    assert code == 1
    assert "pairs=1 conflicting=1" in out
    assert f"1 by hand {REGISTRY}" in out
    assert "a x b" in out


def test_a_pair_that_meets_only_in_a_file_the_merge_rebuilds_passes(repo: Path, capsys) -> None:
    _branch(repo, "a", {GENERATED: '{"a": 1}\n'})
    _branch(repo, "b", {GENERATED: '{"b": 1}\n'})
    code, out = _run(repo, capsys, "a", "b")
    assert code == 0, out
    assert "pairs=1 conflicting=1" in out
    assert f"1 rebuilt {GENERATED}" in out


def test_a_pair_that_also_meets_by_hand_counts_each_file_on_its_side(repo: Path, capsys) -> None:
    _branch(repo, "a", {GENERATED: '{"a": 1}\n', REGISTRY: "one\na\n"})
    _branch(repo, "b", {GENERATED: '{"b": 1}\n', REGISTRY: "one\nb\n"})
    code, out = _run(repo, capsys, "a", "b")
    assert code == 1
    assert f"1 by hand {REGISTRY}" in out
    assert f"1 rebuilt {GENERATED}" in out


def test_every_pair_of_three_heads_is_measured(repo: Path, capsys) -> None:
    for name in "abc":
        _branch(repo, name, {f"docs/feature-{name}.md": "x\n"})
    assert "pairs=3 conflicting=0" in _run(repo, capsys, "a", "b", "c")[1]


def test_one_head_is_refused_for_there_is_no_pair(repo: Path) -> None:
    _branch(repo, "a", {"docs/feature-a.md": "a\n"})
    with pytest.raises(SystemExit, match="two heads"):
        pair_conflicts.main(["--root", str(repo), "a"])


def test_the_default_list_is_the_one_the_merge_rebuilds() -> None:
    assert "tests/data/golden_pins.json" in pair_conflicts.rebuilt_at_merge(ROOT)
