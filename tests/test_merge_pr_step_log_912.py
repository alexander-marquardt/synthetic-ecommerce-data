"""A test that runs scripts/merge_pr.sh and times out names the step it was in (#912).

pytest-timeout's dump of such a case showed only the parent waiting in
``communicate``, so a stalled step and a slow host looked the same (#911). The
script prints a timestamped line to stderr as each step starts, and
``test_merge_pr._run`` keeps the script's output in files, not a pipe. When the
call ends in an exception (a timeout's included) it prints that output and
stops the script's process group.

Here an inner pytest run uses that helper with a step-2 build that never ends,
under a short timeout, and its log must name step 2 as the last step started.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path

# The inner case runs its world and _run; the import puts this file in CI's selection for
# a change to them or to a part of the script (scripts/ci_select.py).
import test_merge_pr  # noqa: F401

TESTS = Path(__file__).resolve().parent

#: The inner case: ``uv`` hangs on the build, so the script stops in step 2. The
#: hung ``sleep`` writes its pid, so the outer case can see it was stopped.
_INNER = """
import os
import sys

sys.path.insert(0, {tests!r})
import pytest
from test_merge_pr import _GREEN, _GREEN_CHECK, _open_pr, _run, world  # noqa: F401


@pytest.mark.timeout({timeout})
def test_the_build_hangs(world, tmp_path):
    hang = tmp_path / "hang"
    hang.mkdir()
    (hang / "uv").write_text(
        "#!/usr/bin/env bash\\n"
        'if [[ " $* " == *" build "* ]]; then echo $$ >{pid_file}; exec sleep 600; fi\\n'
        f'exec {{world["bin"]}}/uv "$@"\\n'
    )
    (hang / "uv").chmod(0o755)
    head = _open_pr(world, _GREEN)
    _run(world, head, _GREEN_CHECK, PATH=f"{{hang}}{{os.pathsep}}{{world['env']['PATH']}}")
"""

#: Seconds the inner case may run, its fixtures not counted: reaching step 2 is
#: a clone and a merge of a small tree, a few seconds.
_TIMEOUT = 20


def _gone(pid: int) -> bool:
    """True once ``pid`` is no longer a process; a stopped one is reaped at once."""
    for _ in range(50):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.1)
    return False


def test_a_step_that_hangs_under_a_test_timeout_is_named_in_the_log(tmp_path: Path) -> None:
    pid_file = tmp_path / "hung.pid"
    inner = tmp_path / "inner"
    inner.mkdir()
    (inner / "test_inner_912.py").write_text(
        _INNER.format(tests=str(TESTS), timeout=_TIMEOUT, pid_file=str(pid_file))
    )
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTEST_", "GEN_LOCAL_CI"))}
    # No config file: none of the suite's addopts (xdist, ...). The signal method, as on CI:
    # the thread method exits the process, and nothing after the timeout runs.
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            os.devnull,
            "--rootdir",
            str(inner),
            "--basetemp",
            str(tmp_path / "base"),
            "-p",
            "no:cacheprovider",
            "-p",
            "no:randomly",
            "-o",
            "timeout_method=signal",
            "-o",
            "timeout_func_only=true",
            str(inner / "test_inner_912.py"),
        ],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    log = result.stdout + result.stderr
    assert "Timeout" in log, f"the inner case did not time out:\n{log[-3000:]}"
    started = re.findall(
        r"^merge_pr\.sh: \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ \+\d+s step (\S+) started: ",
        log,
        flags=re.MULTILINE,
    )
    assert started, f"the timeout's log names no step of merge_pr.sh:\n{log[-3000:]}"
    assert started[-1] == "2", f"the last step started is {started[-1]}, not 2: {started}"
    assert started[:4] == ["lock", "0", "clone", "1"], started
    assert _gone(int(pid_file.read_text())), "the hung build still runs after the timeout"
