"""Core's changed-line mutant runner runs on a clone of this repository (elastic/prism#11680).

The ask was core's ``scripts/mutant_run.py`` with ``--root``, not a second
runner. Core is private and this repository's CI cannot read it, so the runner
and its two companions sit under ``vendor/prism/scripts/`` byte for byte
(``vendor/prism/PIN.txt``). This test runs that copy on a small repository of
its own and reads the verdicts, which is the part of the ask that was untested:
the runner starts the tree's tests with ITS OWN interpreter, so it has to be
started with this repository's (``uv run python``).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "vendor" / "prism" / "scripts" / "mutant_run.py"

LIB = "def add(a, b):\n    return a + b\n\n\ndef unused(a):\n    return a\n"
TEST = "from lib import add\n\n\ndef test_add():\n    assert add(2, 3) == 5\n"
MUTANTS = """\
TESTS = ["tests/test_lib.py"]
PYTEST_ARGS = ["-q", "-p", "no:cacheprovider"]
MUTANTS = [
    ("lib.py", "return a + b", "return a - b", "add-subtracts"),
    ("lib.py", "return a\\n", "return None\\n", "unused-returns-none"),
]
"""


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@example.invalid",
            "-c",
            "commit.gpgsign=false",
            *args,
        ],
        check=True,
        capture_output=True,
    )


@pytest.fixture
def sister(tmp_path: Path) -> Path:
    repo = tmp_path / "sister"
    (repo / "tests").mkdir(parents=True)
    (repo / "lib.py").write_text(LIB, encoding="utf-8")
    (repo / "tests" / "test_lib.py").write_text(TEST, encoding="utf-8")
    (repo / "conftest.py").write_text("", encoding="utf-8")
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    (tmp_path / "mutants.py.txt").write_text(MUTANTS, encoding="utf-8")
    return repo


def test_the_vendored_runner_judges_mutants_in_another_root(sister: Path) -> None:
    assert RUNNER.is_file(), f"{RUNNER} is missing"
    done = subprocess.run(
        [sys.executable, str(RUNNER), str(sister.parent / "mutants.py.txt"), "--root", str(sister)],
        capture_output=True,
        text=True,
        cwd=sister.parent,
        timeout=300,
    )
    out = done.stdout
    assert "KILLED   add-subtracts" in out, out + done.stderr
    assert "SURVIVED unused-returns-none" in out, out
    assert "1 of 2 killed" in out, out
    assert done.returncode == 0, out + done.stderr
    assert (sister / "lib.py").read_text(encoding="utf-8") == LIB


def test_the_runner_writes_nothing_into_the_clone_it_judges(sister: Path) -> None:
    subprocess.run(
        [sys.executable, str(RUNNER), str(sister.parent / "mutants.py.txt"), "--root", str(sister)],
        capture_output=True,
        text=True,
        cwd=sister.parent,
        timeout=300,
    )
    status = subprocess.run(
        ["git", "-C", str(sister), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert RUNNER.is_file(), f"{RUNNER} is missing"
    assert status == ""
