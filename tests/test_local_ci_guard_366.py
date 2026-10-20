"""scripts/local_ci_guard.py bounds a local CI command's memory and runs one at a time (#366).

``merge_pr.sh --local-ci`` sizes the pytest workers at ``WORKER_MB`` each from the memory
available when the steps are emitted (#365), and nothing held that bound while the run went
on. On the shared agent VM an uncapped xdist run took the host down once (2026-10-15 18:27Z),
and two local CI runs could overlap. The guard runs a command under a ceiling of
``workers * WORKER_MB`` (a probe over the process tree, which stops the run and exits 97 when
the tree passes it, so an overrun fails one merge and not the machine) and under a lock that
a second run waits for instead of failing.

Each case starts the real guard on real processes; the ceilings are a few hundred MB so no
case needs the memory it describes for more than a moment.
"""

from __future__ import annotations

import fcntl
import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
GUARD = REPO / "scripts" / "local_ci_guard.py"

_spec = importlib.util.spec_from_file_location("local_ci_guard", GUARD)
assert _spec is not None and _spec.loader is not None
guard = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("local_ci_guard", guard)
_spec.loader.exec_module(guard)

#: Touches ``MB`` megabytes (an untouched allocation is not resident) and then idles, so a
#: run the probe does not stop would take 60 s: the cases below finish in a few.
HOG = "import time; b = bytearray(b'x') * ({mb} * 1024 * 1024); time.sleep(60)"


@pytest.fixture
def env(tmp_path: Path) -> dict[str, str]:
    base = {k: v for k, v in os.environ.items() if not k.startswith(("LOCAL_CI_", "PYTEST_"))}
    return {
        **base,
        "LOCAL_CI_LOCK": str(tmp_path / "ci.lock"),
        "LOCAL_CI_LOCK_POLL": "0.1",
        "LOCAL_CI_LOCK_WAIT": "0",
        "LOCAL_CI_GUARD_POLL": "0.1",
    }


def _guard(env: dict[str, str], *command: str, **extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GUARD), "--", *command],
        env={**env, **extra},
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )


# -- the ceiling ---------------------------------------------------------------


def test_the_ceiling_is_the_workers_times_the_budget_of_one_worker() -> None:
    assert guard.WORKER_MB == 4500
    assert guard.ceiling_mb(8, {}) == 8 * guard.WORKER_MB
    assert guard.ceiling_mb(1, {}) == guard.WORKER_MB


def test_a_ceiling_named_in_the_environment_replaces_the_computed_one() -> None:
    assert guard.ceiling_mb(8, {"LOCAL_CI_MEMORY_MB": "1234"}) == 1234


@pytest.mark.parametrize(
    ("argv", "environ", "expected"),
    [
        (["pytest", "-n", "6"], {}, 6),
        (["pytest", "-n6"], {}, 6),
        (["pytest", "--numprocesses=5"], {}, 5),
        (["pytest", "-n", "6"], {"LOCAL_CI_WORKERS": "3"}, 3),
        (["bash", "-c", "x"], {"LOCAL_CI_WORKERS": "0"}, 1),
    ],
    ids=["n-space-N", "nN", "numprocesses", "variable-wins", "zero-is-one"],
)
def test_the_worker_count_is_the_one_the_command_runs_with(
    argv: list[str], environ: dict[str, str], expected: int
) -> None:
    assert guard.workers_for(argv, environ) == expected


def test_a_command_that_passes_the_ceiling_is_stopped_and_fails(env: dict[str, str]) -> None:
    started = time.monotonic()
    done = _guard(env, sys.executable, "-c", HOG.format(mb=400), LOCAL_CI_MEMORY_MB="200")
    assert done.returncode == guard.EXIT_OVER_CEILING == 97, done.stderr
    assert "memory ceiling" in done.stderr and "200 MB" in done.stderr, done.stderr
    assert time.monotonic() - started < 50, "the run was not stopped when it passed the ceiling"


def test_a_command_under_the_ceiling_runs_to_its_own_exit_code(env: dict[str, str]) -> None:
    done = _guard(
        env,
        sys.executable,
        "-c",
        "import sys; b = bytearray(b'x') * (20 * 1024 * 1024); print('ran'); sys.exit(3)",
        LOCAL_CI_MEMORY_MB="2000",
    )
    assert done.returncode == 3, done.stderr
    assert "ran" in done.stdout


def test_a_descendant_the_command_started_counts_toward_the_ceiling(env: dict[str, str]) -> None:
    """A pytest worker is a child of pytest: the tree is measured, not the first process."""
    outer = (
        f"import subprocess, sys; subprocess.run([sys.executable, '-c', {HOG.format(mb=400)!r}])"
    )
    done = _guard(env, sys.executable, "-c", outer, LOCAL_CI_MEMORY_MB="200")
    assert done.returncode == 97, done.stderr


def test_an_unset_worker_count_is_handed_to_the_command(env: dict[str, str]) -> None:
    """The emitted script reads ``${LOCAL_CI_WORKERS:-N}``: the guard's count is the run's."""
    script = "import os; print(os.environ.get('LOCAL_CI_WORKERS', 'unset'))"
    kept = _guard(env, sys.executable, "-c", script, LOCAL_CI_WORKERS="3")
    assert kept.stdout.strip() == "3"
    given = _guard(env, sys.executable, "-c", script, "-n", "7")
    assert given.stdout.strip() == "7", given.stdout + given.stderr


# -- the lock ------------------------------------------------------------------


def _hold(path: str):
    handle = open(path, "a+")  # noqa: SIM115 (held by the caller until it is closed)
    fcntl.flock(handle, fcntl.LOCK_EX)
    return handle


def test_a_second_run_waits_for_the_first_and_then_runs(
    env: dict[str, str], tmp_path: Path
) -> None:
    marks = tmp_path / "marks"
    first = (
        "import time; time.sleep(2); "
        f"open({str(marks)!r}, 'a').write('first-done %f\\n' % time.time())"
    )
    second = f"import time; open({str(marks)!r}, 'a').write('second-start %f\\n' % time.time())"
    one = subprocess.Popen([sys.executable, str(GUARD), "--", sys.executable, "-c", first], env=env)
    time.sleep(1.0)  # the first holds the lock by now
    done = _guard(env, sys.executable, "-c", second, LOCAL_CI_LOCK_WAIT="60")
    assert one.wait(timeout=60) == 0
    assert done.returncode == 0, done.stderr
    assert "waiting for another local CI run" in done.stderr, done.stderr
    times = {line.split()[0]: float(line.split()[1]) for line in marks.read_text().splitlines()}
    assert times["second-start"] >= times["first-done"], "the two runs overlapped"


def test_a_wait_that_runs_out_refuses_and_names_the_holder(
    env: dict[str, str], tmp_path: Path
) -> None:
    held = _hold(env["LOCAL_CI_LOCK"])
    try:
        ran = tmp_path / "ran"
        done = _guard(env, sys.executable, "-c", f"open({str(ran)!r}, 'w')", LOCAL_CI_LOCK_WAIT="1")
        assert done.returncode == guard.EXIT_LOCK_TIMEOUT == 98, done.stderr
        assert "local CI lock" in done.stderr, done.stderr
        assert not ran.exists(), "the command ran without the lock"
    finally:
        held.close()


def test_the_lock_is_freed_when_the_command_ends(env: dict[str, str]) -> None:
    assert _guard(env, sys.executable, "-c", "pass").returncode == 0
    assert _guard(env, sys.executable, "-c", "pass").returncode == 0
    assert _guard(env, sys.executable, "-c", "import sys; sys.exit(5)").returncode == 5
    assert _guard(env, sys.executable, "-c", "pass").returncode == 0
