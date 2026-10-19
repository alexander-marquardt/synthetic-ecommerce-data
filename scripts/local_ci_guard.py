#!/usr/bin/env python3
"""Run one local CI command under a memory ceiling and a machine-wide lock (#366).

    local_ci_guard.py [--notice-fd N] -- COMMAND [ARGS...]

``scripts/merge_pr.sh --local-ci`` sizes the pytest workers at ``WORKER_MB`` each from the
memory available when the steps are emitted (``local_ci_jobs.default_workers``, #365). That
bound was a plan: nothing held it while the run went on, and on the shared agent VM (88 GB,
10-30 agents starting their own test runs after the emit) an uncapped xdist run had already
taken the host down once (2026-10-15 18:27Z). Every command the merge runs for the local CI
(the checks of step 3, each job of step 5) goes through this guard, which adds two things.

**A ceiling.** The command runs in its own process group, and every half second the guard
sums the resident memory of the whole tree under it (the command, the pytest workers, what
they started). Past ``workers * WORKER_MB`` the group is killed and the guard exits 97, with
the figures on stderr: an overrun fails one job, and so one merge, and not the machine. The
worker count is the command's own: ``LOCAL_CI_WORKERS`` (``0`` is one process), else the
``-n N`` of its arguments, else this machine's ``default_workers()`` now, which is then handed
to the command as ``LOCAL_CI_WORKERS`` so the ``-n`` the emitted script uses is the one the
ceiling was drawn for (the script was emitted before the lock wait, when the memory was
different). ``LOCAL_CI_MEMORY_MB`` replaces the ceiling. Resident memory counts a page shared
by two processes twice, so the figure errs high, not low; the probe is a poll, so a spike
between two looks is for the kernel to meet, as before.

**A lock.** One local CI command runs at a time on the machine (an ``flock`` on
``LOCAL_CI_LOCK``, default ``<tmp>/gen-local-ci.lock``): a second run says so and waits,
polling every ``LOCAL_CI_LOCK_POLL`` seconds (2), and refuses with 98 after
``LOCAL_CI_LOCK_WAIT`` (14400, 4 h) naming the holder. The kernel frees the lock when its
holder ends, however it ends, so no run needs to clean up and none can leave a stale one. It
guards the machine's memory, which is not what ``merge_pr.sh``'s merge lock (#383) guards: the
order of merges into ``main``. It is taken by a ``--dry-run`` too, which runs the same jobs.

Notices go to stderr, or to ``--notice-fd`` (merge_pr.sh points it at its own stderr while the
command's output goes to the job's log), each line starting ``local_ci_guard:``.
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from local_ci_jobs import WORKER_MB, WORKERS_ENV, default_workers  # noqa: E402

#: Exit status of a command stopped for passing its ceiling.
EXIT_OVER_CEILING = 97
#: Exit status of a run that gave up waiting for the lock.
EXIT_LOCK_TIMEOUT = 98

MEMORY_ENV = "LOCAL_CI_MEMORY_MB"
LOCK_ENV = "LOCAL_CI_LOCK"
LOCK_WAIT_ENV = "LOCAL_CI_LOCK_WAIT"
LOCK_POLL_ENV = "LOCAL_CI_LOCK_POLL"
PROBE_ENV = "LOCAL_CI_GUARD_POLL"

_N_OPTION = re.compile(r"^(?:-n|--numprocesses)(?:=|(?=\d))?(\d+)$")


def workers_for(argv: list[str], environ: dict[str, str]) -> int:
    """The pytest workers the command runs with, for the ceiling: the variable, else its ``-n``."""
    named = environ.get(WORKERS_ENV)
    if named not in (None, ""):
        return max(1, int(named))
    for index, arg in enumerate(argv):
        found = _N_OPTION.match(arg)
        if found:
            return max(1, int(found.group(1)))
        if arg in ("-n", "--numprocesses") and index + 1 < len(argv) and argv[index + 1].isdigit():
            return max(1, int(argv[index + 1]))
    return default_workers()


def ceiling_mb(workers: int, environ: dict[str, str]) -> int:
    """The memory the command's whole tree may hold, in MB."""
    named = environ.get(MEMORY_ENV)
    if named not in (None, ""):
        return int(named)
    return workers * WORKER_MB


def tree_mb(root: int) -> int:
    """Resident MB of ``root``, its descendants and the rest of its process group."""
    out = subprocess.run(
        ["ps", "-A", "-o", "pid=", "-o", "ppid=", "-o", "pgid=", "-o", "rss="],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    rows = [tuple(int(x) for x in line.split()) for line in out.splitlines() if line.split()]
    members = {root}
    grew = True
    while grew:
        grew = False
        for pid, ppid, pgid, _ in rows:
            if pid not in members and (ppid in members or pgid == root):
                members.add(pid)
                grew = True
    return sum(rss for pid, _, _, rss in rows if pid in members) // 1024


def _kill_group(pid: int) -> None:
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.killpg(pid, signal.SIGKILL)


class Notices:
    def __init__(self, fd: int) -> None:
        self.fd = fd

    def say(self, text: str) -> None:
        os.write(self.fd, f"local_ci_guard: {text}\n".encode())


def take_lock(environ: dict[str, str], notices: Notices):
    """Hold the machine's local CI lock, waiting for it; None when the wait ran out."""
    path = environ.get(LOCK_ENV) or str(Path(tempfile.gettempdir()) / "gen-local-ci.lock")
    wait = float(environ.get(LOCK_WAIT_ENV, 14400))
    poll = float(environ.get(LOCK_POLL_ENV, 2))
    handle = open(path, "a+", encoding="utf-8")  # noqa: SIM115 (held until the guard exits)
    deadline = time.monotonic() + wait
    said = False
    while True:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except OSError:
            handle.seek(0)
            holder = handle.read().strip() or "an unnamed run"
            if time.monotonic() >= deadline:
                notices.say(
                    f"the local CI lock {path} is held by {holder} and the "
                    f"{wait:g} s wait ran out; NOT run"
                )
                return None
            if not said:
                notices.say(
                    f"waiting for another local CI run (held by {holder}); the lock is {path}"
                )
                said = True
            time.sleep(poll)
    handle.seek(0)
    handle.truncate()
    handle.write(f"pid {os.getpid()}: {' '.join(sys.argv[1:])[:120]}\n")
    handle.flush()
    return handle


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--notice-fd", type=int, default=2)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("no command after --")
    notices = Notices(args.notice_fd)
    environ = dict(os.environ)

    lock = take_lock(environ, notices)
    if lock is None:
        return EXIT_LOCK_TIMEOUT
    workers = workers_for(command, environ)
    ceiling = ceiling_mb(workers, environ)
    child_env = dict(environ)
    if environ.get(WORKERS_ENV) in (None, ""):
        child_env[WORKERS_ENV] = str(workers)
    probe = float(environ.get(PROBE_ENV, 0.5))

    child = subprocess.Popen(command, env=child_env, start_new_session=True)

    def forward(signum: int, _frame: object) -> None:
        _kill_group(child.pid)
        raise SystemExit(128 + signum)

    signal.signal(signal.SIGTERM, forward)
    signal.signal(signal.SIGINT, forward)
    peak = 0
    try:
        while child.poll() is None:
            peak = max(peak, tree_mb(child.pid))
            if peak > ceiling:
                _kill_group(child.pid)
                child.wait()
                notices.say(
                    f"memory ceiling exceeded: the command's tree reached {peak} MB, "
                    f"past the ceiling of {ceiling} MB ({workers} workers x {WORKER_MB} MB; "
                    f"{MEMORY_ENV} replaces it); stopped"
                )
                return EXIT_OVER_CEILING
            time.sleep(probe)
    finally:
        _kill_group(child.pid)  # nothing the command started outlives it
    notices.say(f"peak {peak} MB of a {ceiling} MB ceiling ({workers} workers)")
    return child.returncode


if __name__ == "__main__":
    sys.exit(main())
