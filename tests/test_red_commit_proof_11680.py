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
import yaml

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
    assert "collection failed" in done.stdout


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


def test_the_callers_pytest_options_do_not_reach_the_judged_run(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The local CI runs the suite with PYTEST_ADDOPTS="-n N --dist loadgroup"; under xdist a
    # name that selects nothing exits 5 with no outcomes, which read as NOT JUDGED, not REFUSED.
    monkeypatch.setenv("PYTEST_ADDOPTS", "-n 2 --dist loadgroup")
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
    assert "must name tests as path.py::name; it names the, new, test" in done.stdout


def test_a_trailer_that_names_nothing_never_runs_the_whole_suite(repo: Path) -> None:
    base = _base(repo)
    _commit(repo, GREEN, "empty\n\nRefs #1\n\nRed-Test: ,")
    done = _prove(repo, base)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "it names no test id" in done.stdout


def test_a_file_whose_name_starts_with_none_is_not_a_none_trailer(repo: Path) -> None:
    base = _base(repo)
    (repo / "none_tests.py").write_text(RED, encoding="utf-8")
    _commit(repo, None, "none\n\nRefs #1\n\nRed-Test: none_tests.py::test_red")
    done = _prove(repo, base)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "PROVEN" in done.stdout and "none_tests.py::test_red" in done.stdout


def test_commits_are_judged_oldest_first(repo: Path) -> None:
    base = _base(repo)
    _commit(repo, RED, "first\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_red")
    first = _git(repo, "rev-parse", "--short=9", "HEAD")
    _commit(repo, RED, "second\n\nRefs #2\n\nRed-Test: tests/test_x.py::test_red")
    second = _git(repo, "rev-parse", "--short=9", "HEAD")
    done = _prove(repo, base)
    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stdout.index(first) < done.stdout.index(second)


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


def test_a_none_reason_that_wraps_onto_a_second_line_is_still_none(repo: Path) -> None:
    base = _base(repo)
    wrapped = "docs\n\nRefs #1\n\nRed-Test: none \u2014 a reason long enough\n  that it wraps"
    _commit(repo, RAISES, wrapped)
    done = _prove(repo, base)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "REFUSED" not in done.stdout


def test_a_merge_commit_is_never_judged_whatever_its_message_declares(repo: Path) -> None:
    _commit(repo, GREEN, "green test\n\nRefs #1")
    base = _base(repo)
    _git(repo, "switch", "-q", "-c", "side")
    (repo / "side.txt").write_text("side\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "side")
    _git(repo, "switch", "-q", "main")
    (repo / "main.txt").write_text("main\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "main")
    merge = "merge\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_green"
    _git(repo, "merge", "-q", "--no-ff", "side", "-m", merge)
    done = _prove(repo, base)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "REFUSED" not in done.stdout and "PROVEN" not in done.stdout


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
    assert done.returncode == _prove(repo, "no-such-ref").returncode


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


def test_the_commits_own_packages_are_the_ones_imported(repo: Path, tmp_path: Path) -> None:
    """A stale copy of a package on the caller's path must not stand in for the commit's."""
    stale = tmp_path / "stale"
    (stale / "pkg").mkdir(parents=True)
    (stale / "pkg" / "__init__.py").write_text("VALUE = 1\n", encoding="utf-8")
    base = _base(repo)
    (repo / "src" / "pkg").mkdir(parents=True)
    (repo / "src" / "pkg" / "__init__.py").write_text("VALUE = 2\n", encoding="utf-8")
    _commit(
        repo,
        "from pkg import VALUE\n\n\ndef test_red():\n    assert VALUE == 1\n",
        "pkg\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_red",
    )
    env = {**os.environ, "PYTHONPATH": str(stale)}
    done = subprocess.run(
        [sys.executable, str(PROOF), "--repo", str(repo), "--range", f"{base}..HEAD"],
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
    )
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_run_that_writes_no_outcomes_is_not_judged_rather_than_passed(repo: Path) -> None:
    base = _base(repo)
    stuck = "raise RuntimeError('no tests can start')\n"
    (repo / "conftest.py").write_text(stuck, encoding="utf-8")
    _commit(repo, RED, "stuck\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_red")
    done = _prove(repo, base)
    assert done.returncode == 3, done.stdout + done.stderr
    assert "NOT JUDGED" in done.stdout and "wrote no outcomes" in done.stdout


def test_a_run_past_the_time_limit_is_not_judged(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    base = _base(repo)
    _commit(
        repo,
        "import time\n\n\ndef test_red():\n    time.sleep(60)\n    assert 1 == 2\n",
        "slow\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_red",
    )
    proof = _proof()
    monkeypatch.setattr(proof, "TIMEOUT_SECS", 2)
    assert proof.main(["--repo", str(repo), "--range", f"{base}..HEAD"]) == 3
    assert "ran longer than 2 s" in capsys.readouterr().out


def test_the_workflow_runs_the_proof_over_the_pull_requests_commits() -> None:
    workflow = yaml.safe_load((ROOT / ".github" / "workflows" / "ci.yaml").read_text())
    job = workflow["jobs"]["red-commit-proof"]
    assert job["if"] == (
        "github.event_name == 'pull_request' ||"
        " (github.event_name == 'workflow_dispatch' && inputs.head != '')"
    )
    assert job["steps"][0]["with"] == {"fetch-depth": 0}, "the base must be reachable"
    command = " ".join(step["run"] for step in job["steps"] if "run" in step)
    assert "scripts/red_commit_proof.py" in command
    assert "github.event.pull_request.base.sha" in command
    assert "github.event.pull_request.head.sha" in command


def test_the_documented_commands_name_files_that_exist() -> None:
    doc = (ROOT / "docs" / "red-commit-and-mutants.md").read_text(encoding="utf-8")
    for path in ("scripts/red_commit_proof.py", "vendor/prism/scripts/mutant_run.py"):
        assert path in doc
        assert (ROOT / path).is_file(), path


# ---- red commits made before the checker landed are grandfathered (gen#432) ----
#
# The cutoff is ANCESTRY, not a date: a commit that is not a descendant of the
# commit that introduced the checker (``CUTOFF``) was written before the rule
# existed, so any failure of its named tests is red enough. Each case builds a
# throwaway history and names its own cutoff with ``--cutoff``.

STOPS = "def test_red():\n    next(iter([]))\n    assert 1 == 2\n"
KEY = "def test_red():\n    {}['missing']\n    assert 1 == 2\n"
SETUP = (
    "import pytest\n\n\n@pytest.fixture\ndef broken():\n    raise RuntimeError('setup')\n\n\n"
    "def test_red(broken):\n    assert 1 == 2\n"
)
RED_TRAILER = "red\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_red"


def _cutoff(repo: Path) -> str:
    return _commit(repo, None, "the commit that introduced the checker\n\nRefs #1")


def _prove_with(repo: Path, base: str, cutoff: str) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    return subprocess.run(
        [
            sys.executable,
            str(PROOF),
            "--repo",
            str(repo),
            "--cutoff",
            cutoff,
            "--range",
            f"{base}..HEAD",
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
    )


@pytest.mark.parametrize("source", [STOPS, KEY, SETUP], ids=["StopIteration", "KeyError", "setup"])
def test_a_red_commit_before_the_cutoff_may_fail_on_anything(repo: Path, source: str) -> None:
    base = _base(repo)
    _commit(repo, source, RED_TRAILER)
    cutoff = _cutoff(repo)
    done = _prove_with(repo, base, cutoff)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "GRANDFATHERED" in done.stdout and "REFUSED" not in done.stdout


def test_a_red_commit_after_the_cutoff_that_fails_on_stop_iteration_is_refused(
    repo: Path,
) -> None:
    cutoff = _cutoff(repo)
    base = _base(repo)
    _commit(repo, STOPS, RED_TRAILER)
    done = _prove_with(repo, base, cutoff)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "REFUSED" in done.stdout and "GRANDFATHERED" not in done.stdout
    assert "not on an assertion" in done.stdout


def test_a_red_commit_after_the_cutoff_that_fails_on_an_assertion_is_proven(repo: Path) -> None:
    cutoff = _cutoff(repo)
    base = _base(repo)
    _commit(repo, RED, RED_TRAILER)
    done = _prove_with(repo, base, cutoff)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "PROVEN" in done.stdout and "GRANDFATHERED" not in done.stdout


def test_one_range_judges_each_side_of_the_cutoff_by_its_own_rule(repo: Path) -> None:
    base = _base(repo)
    _commit(repo, STOPS, "before\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_red")
    cutoff = _cutoff(repo)
    _commit(repo, RED, "after\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_red")
    done = _prove_with(repo, base, cutoff)
    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stdout.count("GRANDFATHERED") == 1 and done.stdout.count("PROVEN") == 1
    assert "before the checker landed" in done.stdout


def test_the_cutoff_is_ancestry_so_a_late_author_date_does_not_hide_an_old_commit(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = _base(repo)
    monkeypatch.setenv("GIT_AUTHOR_DATE", "2099-01-01T00:00:00+00:00")
    _commit(repo, STOPS, RED_TRAILER)
    monkeypatch.delenv("GIT_AUTHOR_DATE")
    cutoff = _cutoff(repo)
    done = _prove_with(repo, base, cutoff)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "GRANDFATHERED" in done.stdout


def test_a_pre_cutoff_test_that_passes_or_matches_nothing_is_still_refused(repo: Path) -> None:
    base = _base(repo)
    _commit(repo, GREEN, "not red\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_green")
    _commit(repo, GREEN, "typo\n\nRefs #1\n\nRed-Test: tests/test_x.py::test_nothing")
    cutoff = _cutoff(repo)
    done = _prove_with(repo, base, cutoff)
    assert done.returncode == 1, done.stdout + done.stderr
    assert done.stdout.count("REFUSED") == 2 and "GRANDFATHERED" not in done.stdout


def test_the_cutoff_constant_is_a_full_sha_and_the_docs_name_it() -> None:
    cutoff = _proof().CUTOFF
    assert len(cutoff) == 40 and set(cutoff) <= set("0123456789abcdef"), cutoff
    doc = (ROOT / "docs" / "red-commit-and-mutants.md").read_text(encoding="utf-8")
    assert cutoff in doc
