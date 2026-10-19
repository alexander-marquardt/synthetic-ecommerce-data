"""No file under git is build output (gen#536).

``golden-retail/stats.json``, the sneak-peek samples and previews and the two generated docs
moved with every retail PR, so each PR that committed one conflicted the rest and main went red
whenever a merge did not roll them. CI builds them as artifacts now (``scripts/build_derived.py``).
``scripts/check_no_derived_files.py`` is the guard that keeps them out: these tests plant each one
in a throwaway repository and read the real tree.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_no_derived_files as guard  # noqa: E402

RD = "prototypes/retail_drawings"
#: One concrete path for every glob the guard names, and the ones that were committed.
PLANTED = (
    "golden-retail/stats.json",
    "docs/figures.md",
    "docs/retail-apparel-decoys.md",
    f"{RD}/samples.ndjson",
    f"{RD}/samples4.ndjson",
    f"{RD}/preview.html",
    f"{RD}/preview4.html",
    f"{RD}/samples_next.ndjson",
)


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
         "-c", "commit.gpgsign=false", *args],
        capture_output=True,
        text=True,
    )  # fmt: skip
    assert done.returncode == 0, f"git {args}: {done.stderr}"
    return done.stdout


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    (root / "README.md").write_text("hello\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    return root


@pytest.mark.parametrize("path", PLANTED)
def test_a_re_added_derived_file_fails_the_check_and_is_named(path, repo, capsys) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{}\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "re-add")
    assert guard.main(["--root", str(repo)]) == 1
    assert path in capsys.readouterr().out


def test_a_tree_with_no_derived_file_passes(repo, capsys) -> None:
    (repo / "docs").mkdir()
    (repo / "docs" / "retail-prototype.md").write_text("a doc\n", encoding="utf-8")
    (repo / "golden-retail").mkdir()
    (repo / "golden-retail" / "other.json").write_text("{}\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "docs")
    assert guard.main(["--root", str(repo)]) == 0
    assert capsys.readouterr().out == ""


def test_this_repository_tracks_no_derived_file() -> None:
    tracked = _git(ROOT, "ls-files").split("\n")
    assert guard.offenders(tracked) == []
