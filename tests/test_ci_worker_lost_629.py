"""A CI shard that loses its xdist workers is an infra failure, rerun once (#629).

Three pull requests had a ``tests`` shard end red with no test id: both xdist workers went
down within a tenth of a second ("node down: Not properly terminated"), pytest's controller then
raised ``INTERNALERROR> KeyError: <WorkerController gw2>`` while it tried to replace them, and
the verdict read as a test failure. Main's same shard was green. Nothing a test did was named.

``scripts/ci_run_pytest.py`` runs the shard's pytest command. When the run shows a lost worker it
says ``infra: worker lost``, prints what the runner can show about memory, and runs the command
once more; a run that loses a worker twice ends with its own exit code, not a test's. A run whose
tests failed, with every worker alive, is not rerun: a failing test stays a failing test.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "ci_run_pytest.py"
WORKFLOW = REPO / ".github" / "workflows" / "ci.yaml"

_spec = importlib.util.spec_from_file_location("ci_run_pytest", SCRIPT)
assert _spec is not None and _spec.loader is not None
ci_run_pytest = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("ci_run_pytest", ci_run_pytest)
_spec.loader.exec_module(ci_run_pytest)

#: What shard 7 of run 39608972042 printed (job 119344738657), trimmed to its signature lines.
LOST_LOG = """\
created: 2/2 workers
2 workers [845 items]
.............................................[gw1] node down: Not properly terminated
F
replacing crashed worker gw1
[gw0] node down: Not properly terminated
F
replacing crashed worker gw0
INTERNALERROR> KeyError: <WorkerController gw2>
"""

#: A real failure: a test asserted, every worker alive.
FAILED_LOG = """\
2 workers [845 items]
..F.....
=========================== short test summary info ============================
FAILED tests/test_a.py::test_one - assert 1 == 2
========================= 1 failed, 844 passed in 61.10s =======================
"""

FAKE = """\
import pathlib, sys
counter, mode = pathlib.Path(sys.argv[1]), sys.argv[2]
runs = int(counter.read_text()) + 1 if counter.exists() else 1
counter.write_text(str(runs))
lost = "[gw0] node down: Not properly terminated\\n"
lost += "INTERNALERROR> KeyError: <WorkerController gw2>\\n"
if mode == "ok" or (mode == "lose-once" and runs > 1):
    print("845 passed")
elif mode == "fail":
    print("FAILED tests/test_a.py::test_one - assert 1 == 2")
    sys.exit(1)
elif mode == "fail-quoting-the-signature":
    print("E   AssertionError: assert 'expected' in '[gw0] node down: Not properly terminated'")
    print("E   INTERNALERROR> KeyError: <WorkerController gw2>")
    print("AssertionError: assert 'x' in '[gw0] node down: Not properly terminated\\n'")
    sys.exit(1)
else:
    print(lost, end="")
    sys.exit(3)
"""


def run_wrapper(tmp_path: Path, mode: str) -> tuple[subprocess.CompletedProcess[str], int]:
    fake = tmp_path / "fake.py"
    fake.write_text(FAKE, encoding="utf-8")
    counter = tmp_path / "runs"
    done = subprocess.run(
        [sys.executable, str(SCRIPT), "--", sys.executable, str(fake), str(counter), mode],
        capture_output=True,
        text=True,
        check=False,
    )
    return done, int(counter.read_text())


def test_the_log_of_the_lost_workers_is_recognised() -> None:
    assert ci_run_pytest.worker_lost(LOST_LOG)


@pytest.mark.parametrize(
    "text",
    [FAILED_LOG, "", "845 passed in 61.10s", "INTERNALERROR> KeyError: 'fixture'"],
)
def test_a_log_without_a_lost_worker_is_not_one(text: str) -> None:
    assert not ci_run_pytest.worker_lost(text)


def test_a_lost_worker_runs_the_shard_once_more_and_a_pass_is_a_pass(tmp_path: Path) -> None:
    done, runs = run_wrapper(tmp_path, "lose-once")
    assert (done.returncode, runs) == (0, 2), done.stdout
    assert "infra: worker lost" in done.stdout


def test_a_worker_lost_twice_ends_with_the_infra_exit_code_not_a_test_failure(
    tmp_path: Path,
) -> None:
    done, runs = run_wrapper(tmp_path, "lose-always")
    assert (done.returncode, runs) == (ci_run_pytest.EXIT_INFRA, 2), done.stdout
    assert "infra: worker lost" in done.stdout


def test_a_failing_test_is_not_rerun(tmp_path: Path) -> None:
    done, runs = run_wrapper(tmp_path, "fail")
    assert (done.returncode, runs) == (1, 1), done.stdout
    assert "infra: worker lost" not in done.stdout


def test_a_failure_that_quotes_the_signature_is_still_a_failure(tmp_path: Path) -> None:
    done, runs = run_wrapper(tmp_path, "fail-quoting-the-signature")
    assert (done.returncode, runs) == (1, 1), done.stdout
    assert "infra:" not in done.stdout


@pytest.mark.parametrize(
    "line",
    [
        "E   assert 'a' in '[gw0] node down: Not properly terminated'",
        "AssertionError: assert 'x' in '[gw0] node down: Not properly terminated\\n'",
        "    LOG = \"[gw0] node down: Not properly terminated\"",
        "E   INTERNALERROR> KeyError: <WorkerController gw2>",
    ],
)
def test_a_line_that_only_quotes_a_signature_is_not_a_lost_worker(line: str) -> None:
    assert not ci_run_pytest.worker_lost(line)


def test_a_green_run_prints_no_memory_evidence(tmp_path: Path) -> None:
    done, _ = run_wrapper(tmp_path, "ok")
    assert "ci_run_pytest: attempt" not in done.stdout


def test_a_green_run_runs_once(tmp_path: Path) -> None:
    done, runs = run_wrapper(tmp_path, "ok")
    assert (done.returncode, runs) == (0, 1), done.stdout
    assert "infra:" not in done.stdout


def test_the_evidence_names_the_cgroup_s_oom_kills_and_peak_memory(tmp_path: Path) -> None:
    (tmp_path / "memory.events").write_text(
        "low 0\nhigh 0\nmax 0\noom 2\noom_kill 2\noom_group_kill 0\n", encoding="utf-8"
    )
    (tmp_path / "memory.peak").write_text(str(3 * 1024**3), encoding="utf-8")
    (tmp_path / "memory.max").write_text("4294967296\n", encoding="utf-8")
    text = "\n".join(ci_run_pytest.evidence(tmp_path))
    assert "oom_kill=2" in text
    assert "peak=3072 MB" in text
    assert "limit=4096 MB" in text


def test_the_evidence_of_a_runner_with_no_cgroup_files_says_so(tmp_path: Path) -> None:
    text = "\n".join(ci_run_pytest.evidence(tmp_path))
    assert "no cgroup memory files" in text


def test_the_tests_step_runs_pytest_through_the_wrapper() -> None:
    steps = WORKFLOW.read_text(encoding="utf-8").split("  main-merged-tree:")[0]
    lines = [ln.strip() for ln in steps.splitlines() if "uv run --locked pytest" in ln]
    assert lines, "the tests job no longer runs pytest"
    assert all(ln.startswith("python3 scripts/ci_run_pytest.py -- ") for ln in lines), lines
