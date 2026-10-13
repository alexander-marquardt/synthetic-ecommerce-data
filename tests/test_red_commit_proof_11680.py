"""CI proves each declared red commit is red on an assertion (elastic/prism#11680, lever #10028).

A pull request's commit that carries a ``Red-Test:`` trailer claims "these tests
fail here, on an assertion". ``scripts/red_commit_proof.py`` checks the claim:
for each such commit it checks the commit's tree out and runs ONLY the named
tests, and refuses unless each one failed on an assertion in its own call
phase. A commit with no trailer, or ``Red-Test: none - <reason>``, runs nothing.

Each case builds a small repository whose tests need nothing from this one.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "scripts" / "red_commit_proof.py"

RED = "def test_red():\n    assert 1 == 2\n"
GREEN = "def test_green():\n    assert 1 == 1\n"
BROKEN_IMPORT = "import not_a_real_module_11680\n\n\ndef test_red():\n    assert 1 == 2\n"
RAISES = "def test_red():\n    raise ValueError('not an assertion')\n"
PARAM = (
    "import pytest\n\n\n"
    "@pytest.mark.parametrize(\n"
    "    'left, right',\n"
    "    [pytest.param(1, 2, id='one, two'), pytest.param(3, 3, id='same')],\n"
    ")\n"
    "def test_case(left, right):\n    assert left == right\n"
)


def _proof() -> ModuleType:
    spec = importlib.util.spec_from_file_location("red_commit_proof", PROOF)
    assert spec is not None and spec.loader is not None, f"{PROOF} is missing"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(
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
        text=True,
    )
    return done.stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    path = tmp_path / "repo"
    path.mkdir()
    _git(path, "init", "-q", "-b", "main")
    (path / "README.md").write_text("base\n", encoding="utf-8")
    _git(path, "add", "-A")
    _git(path, "commit", "-q", "-m", "base")
    return path


def _commit(repo: Path, test_source: str | None, message: str) -> str:
    if test_source is not None:
        (repo / "tests").mkdir(exist_ok=True)
        (repo / "tests" / "test_x.py").write_text(test_source, encoding="utf-8")
    (repo / "marker.txt").write_text(message, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def _prove(repo: Path, base: str) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    return subprocess.run(
        [sys.executable, str(PROOF), "--repo", str(repo), "--range", f"{base}..HEAD"],
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
    )


def _base(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD")


def test_a_test_red_on_an_assertion_is_proven(repo: Path) -> None:
    base = _base(repo)
    _commit(repo, RED, "red\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_red")
    done = _prove(repo, base)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "PROVEN" in done.stdout and "tests/test_x.py::test_red" in done.stdout


def test_a_named_test_that_passes_is_refused(repo: Path) -> None:
    base = _base(repo)
    _commit(repo, GREEN, "not red\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_green")
    done = _prove(repo, base)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "REFUSED" in done.stdout and "tests/test_x.py::test_green" in done.stdout
    assert "passes" in done.stdout


def test_a_collection_error_is_not_a_red_test(repo: Path) -> None:
    base = _base(repo)
    _commit(repo, BROKEN_IMPORT, "broken\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_red")
    done = _prove(repo, base)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "REFUSED" in done.stdout and "tests/test_x.py::test_red" in done.stdout


def test_an_exception_that_is_not_an_assertion_is_refused(repo: Path) -> None:
    base = _base(repo)
    _commit(repo, RAISES, "raises\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_red")
    done = _prove(repo, base)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "REFUSED" in done.stdout and "ValueError" in done.stdout


def test_a_name_that_matches_no_test_is_refused(repo: Path) -> None:
    base = _base(repo)
    _commit(repo, RED, "typo\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_rde")
    done = _prove(repo, base)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "tests/test_x.py::test_rde" in done.stdout and "no test" in done.stdout


def test_prose_in_the_trailer_is_refused(repo: Path) -> None:
    base = _base(repo)
    _commit(repo, RED, "prose\n\nRefs #1\n\nRed-Test: the new test")
    done = _prove(repo, base)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "REFUSED" in done.stdout


def test_a_trailer_naming_one_red_and_one_passing_test_is_refused(repo: Path) -> None:
    base = _base(repo)
    _commit(
        repo,
        RED + "\n\n" + GREEN,
        "two\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_red, tests/test_x.py::test_green",
    )
    done = _prove(repo, base)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "tests/test_x.py::test_green" in done.stdout and "passes" in done.stdout


def test_each_parametrized_case_is_judged_by_its_own_id(repo: Path) -> None:
    base = _base(repo)
    _commit(
        repo,
        PARAM,
        "param\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_case[one, two]",
    )
    done = _prove(repo, base)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "PROVEN" in done.stdout


def test_a_passing_parametrized_case_is_refused(repo: Path) -> None:
    base = _base(repo)
    _commit(
        repo,
        PARAM,
        "param\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_case[same]",
    )
    done = _prove(repo, base)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "passes" in done.stdout


def test_a_none_trailer_and_a_commit_without_one_run_nothing(repo: Path) -> None:
    base = _base(repo)
    _commit(repo, RAISES, "docs\n\nRefs #1\n\nRed-Test: none — docs only")
    _commit(repo, None, "plain")
    done = _prove(repo, base)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "PROVEN" not in done.stdout and "REFUSED" not in done.stdout


def test_the_fix_after_the_red_commit_is_not_judged(repo: Path) -> None:
    base = _base(repo)
    _commit(repo, RED, "red\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_red")
    _commit(repo, "def test_red():\n    assert 1 == 1\n", "fix\n\nRefs #1")
    done = _prove(repo, base)
    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stdout.count("PROVEN") == 1


def test_an_empty_range_is_not_a_pass(repo: Path) -> None:
    done = _prove(repo, _base(repo))
    assert done.returncode == 2, done.stdout + done.stderr
    assert "no commits" in done.stderr


def test_the_judged_tree_is_the_commits_not_the_checkouts(repo: Path) -> None:
    """The fix is on HEAD; the proof still judges the red commit's own tree."""
    base = _base(repo)
    _commit(repo, RED, "red\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_red")
    _commit(repo, "def test_red():\n    assert 1 == 1\n", "fix\n\nRefs #1")
    assert (repo / "tests" / "test_x.py").read_text(encoding="utf-8").endswith("== 1\n")
    done = _prove(repo, base)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "PROVEN" in done.stdout


A = "tests/test_a.py::t"
B = "tests/test_b.py::u"


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([A], [A]),
        ([f"{A}, {B}"], [A, B]),
        ([f"{A} {B}"], [A, B]),
        ([f"{A}[x, y], {B}"], [f"{A}[x, y]", B]),
        ([A, B], [A, B]),
        (["none \u2014 a refactor"], []),
        (["None - docs"], []),
        ([], []),
    ],
)
def test_the_trailer_tokens(values: list[str], expected: list[str]) -> None:
    assert _proof().declared_tests(values) == expected
