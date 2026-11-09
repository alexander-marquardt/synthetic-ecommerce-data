"""A CI shard that the job's timeout ends still prints its memory and kernel-OOM evidence (#918).

Shards whose xdist workers the runner host OOM-killed hung until the job's 25-minute timeout.
``scripts/ci_run_pytest.py`` printed its memory and kernel-OOM lines only after pytest exited,
and the hung pytest never did, so the job log said only "timed out". The cause was read from the
host's ``journalctl -k``, which a CI reader cannot see.

The wrapper now prints that evidence while pytest runs: a trap on SIGTERM, SIGINT and SIGHUP
prints it before the wrapper stops, and a timer (``--evidence-every``) prints it every few minutes,
which is what still shows when the runner ends the step with SIGKILL. A stub ``dmesg`` on PATH
stands in for the kernel log, so each test reads its OOM line in the captured output.
"""

from __future__ import annotations

import contextlib
import importlib.util
import os
import signal
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "ci_run_pytest.py"

#: The kernel's OOM line, as the stub ``dmesg`` prints it.
OOM_LINE = "[12345.6] Out of memory: Killed process 4242 (python) total-vm:9000000kB"
#: A pytest that hangs: it says it started, then sleeps past every test's patience.
HUNG_PYTEST = "import time; print('pytest running', flush=True); time.sleep(30)"


Stop = Callable[[subprocess.Popen[str]], None]


def run_until(tmp_path: Path, opts: list[str], stop: Stop) -> tuple[int, str]:
    """Run the wrapper over a hung pytest, end it with ``stop``: its exit code and whole log."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    dmesg = bin_dir / "dmesg"
    dmesg.write_text(f"#!/bin/sh\necho '{OOM_LINE}'\n", encoding="utf-8")
    dmesg.chmod(0o755)
    env = os.environ | {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}
    command = [sys.executable, str(SCRIPT), *opts, "--", sys.executable, "-c", HUNG_PYTEST]
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env,
        start_new_session=True,
    )  # fmt: skip
    assert proc.stdout is not None
    try:
        first = proc.stdout.readline()
        stop(proc)
        try:
            rest, _ = proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(proc.pid, signal.SIGKILL)
            rest, _ = proc.communicate()
    finally:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(proc.pid, signal.SIGKILL)
    return proc.wait(), first + rest


def test_a_shard_ended_by_the_timeout_prints_the_oom_lines(tmp_path: Path) -> None:
    code, log = run_until(tmp_path, [], lambda proc: proc.send_signal(signal.SIGTERM))
    assert OOM_LINE in log, log
    assert "ci_run_pytest: SIGTERM at " in log, log
    assert "oom_kill=" in log or "no cgroup memory files" in log, log
    assert code == 128 + signal.SIGTERM, log


def test_the_timer_prints_the_oom_lines_before_a_kill_no_trap_can_catch(tmp_path: Path) -> None:
    def kill_after_two_periods(proc: subprocess.Popen[str]) -> None:
        time.sleep(2.5)
        with contextlib.suppress(ProcessLookupError):
            os.killpg(proc.pid, signal.SIGKILL)

    _, log = run_until(tmp_path, ["--evidence-every", "1"], kill_after_two_periods)
    assert OOM_LINE in log, log
    assert "ci_run_pytest: pytest still running at " in log, log


def test_the_evidence_names_the_cgroup_s_memory_in_use_now(tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location("ci_run_pytest_918", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    (tmp_path / "memory.current").write_text(str(5 * 1024**3), encoding="utf-8")
    (tmp_path / "memory.max").write_text("max\n", encoding="utf-8")
    text = "\n".join(module.evidence(tmp_path))
    assert "now=5120 MB" in text, text
    assert "largest finished process: " in text, text


def test_a_green_run_shorter_than_the_period_prints_no_evidence(tmp_path: Path) -> None:
    done = subprocess.run(
        [sys.executable, str(SCRIPT), "--", sys.executable, "-c", "print('ok')"],
        capture_output=True, text=True, timeout=60, check=False,
    )  # fmt: skip
    assert (done.returncode, done.stdout) == (0, "ok\n"), done.stdout + done.stderr
