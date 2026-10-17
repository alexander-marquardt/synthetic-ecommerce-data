"""Run a command with a time limit that ends its whole process group (#10290).

``subprocess.run(timeout=)`` ends the one process it started. A ``docker``
CLI runs ``compose`` and ``buildx`` as plugin child processes and a credential
helper on ``pull`` / ``push``, so that limit left the plugin running with
ppid 1. :func:`run_bounded` starts the command as the leader of a new session
and, when the wait ends early, stops the group: SIGTERM, a short grace, SIGKILL,
then it reaps the leader.

WHAT ENDS THE GROUP: the limit passing, on whichever thread waits; any
exception raised in the waiting thread; and Ctrl-C, SIGTERM or SIGHUP delivered
to this process while it waits ON THE MAIN THREAD, and a SIGTERM or SIGHUP that
ends this process by default while it waits on another thread (through the
watcher below, after the grace). One that arrives while the
command is being started is held until ``Popen`` has returned, then raised
again, so it too ends the group (#10460). A second such signal during the grace
cuts the grace short: SIGKILL is sent at once.

SIGKILL of this process, which runs nothing, and the default end by SIGTERM or
SIGHUP off the main thread are covered by a watcher (#10305): a
small python process in a session of its own, started after the command, that
blocks reading a pipe whose write end only this process holds. When this process
dies by any means the read returns, and the watcher stops the command's group the
way :func:`stop_group` does. On every exit the watcher is killed and reaped
BEFORE its pipe closes, so the group id of a finished command is never signalled.
A watcher is one more process per call, started in the same held window as the
command.

"The group" is processes. A container that ``docker run`` or ``docker compose
up -d`` started belongs to the daemon and is not stopped.

WHAT DOES NOT, said so the guarantee is not over-read:

* Ctrl-C, or a SIGTERM / SIGHUP this process handles without exiting, while the
  wait is on a thread other than the main one: Python runs signal handlers, and
  raises ``KeyboardInterrupt``, on the main thread only, and a handler cannot be
  installed from another. A SIGTERM / SIGHUP that ends the process by default
  there ends the group through the watcher.
* Ctrl-C in a caller whose SIGINT disposition is ``SIG_DFL`` rather than
  Python's ``default_int_handler``: it ends the caller with no exception.
* A descendant that leaves the group itself (its own ``setsid``).
* A further signal in the instant between the SIGKILL and the reap: the group
  has been killed, and its leader may be left unreaped.
* An ending signal (SIGKILL, or a SIGTERM / SIGHUP) that lands in the instant
  between the command's end and the watcher's kill (``_end_watcher``): the
  watcher then signals a group id that may already belong to another process.

Shared by ``tests/fixtures/docker-es/helpers/docker_cli.py`` and
``.github/scripts/check_interpreter_floor.py``; both reach it through a
``sys.path`` insert of ``scripts/``.
``tests/test_bounded_process_ends_the_group_10290.py`` holds the behaviour;
``tests/test_docker_subprocess_has_timeout_10290.py`` refuses a docker command
handed to anything else.
"""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
import sys
import threading
import time
from collections.abc import Callable, Iterator, Mapping, Sequence
from pathlib import Path
from types import FrameType
from typing import Any

#: How long the group gets to exit on SIGTERM before SIGKILL. Shorter than the
#: 10 s ``scripts/heavy_lock.py`` gives its own group after SIGTERM, so a caller
#: stopped by the lock's cap still finishes this before its own SIGKILL arrives.
GROUP_STOP_GRACE_SECONDS = 2.0

#: The status :func:`run_bounded_status` reports for a limit that passed: the
#: one ``timeout(1)`` and ``scripts/heavy_lock.py`` use.
EXPIRED_STATUS = 124

#: What the watcher runs: wait for end of input on stdin, then stop group
#: ``argv[1]`` as :func:`stop_group` does, with ``argv[2]`` seconds of grace.
_WATCHER = (
    "import os, signal, sys, time\n"
    "pgid, grace = int(sys.argv[1]), float(sys.argv[2])\n"
    "sys.stdin.buffer.read()\n"
    "for signum, wait in ((signal.SIGTERM, grace), (signal.SIGKILL, 0)):\n"
    "    try:\n"
    "        os.killpg(pgid, signum)\n"
    "    except (ProcessLookupError, PermissionError):\n"
    "        pass\n"
    "    time.sleep(wait)\n"
)

#: Signals that end a waiting caller by default, and so would orphan the group.
_ENDING_SIGNALS = (signal.SIGTERM, signal.SIGHUP)

#: Signals held while ``Popen`` starts the command. Ctrl-C is among them: its
#: ``KeyboardInterrupt`` raised inside ``Popen`` would leave a running group
#: that nothing holds, as surely as a default SIGTERM would.
_HELD_DURING_START = (signal.SIGINT, *_ENDING_SIGNALS)


#: What ``signal.getsignal`` returns and ``signal.signal`` takes back.
_Handler = Callable[[int, FrameType | None], Any] | int | signal.Handlers | None


class _Signalled(BaseException):
    """An ending signal arrived during the wait; carries which one."""

    def __init__(self, signum: int) -> None:
        super().__init__(signum)
        self.signum = signum


def _raise_signalled(signum: int, _frame: FrameType | None) -> None:
    raise _Signalled(signum)


@contextlib.contextmanager
def _ending_signals_raise() -> Iterator[None]:
    """Turn SIGTERM / SIGHUP into an exception for the length of the wait.

    A signal the caller already ignores stays ignored. Off the main thread this
    does nothing: ``signal.signal`` is refused there.
    """
    previous: dict[signal.Signals, _Handler] = {}
    if threading.current_thread() is threading.main_thread():
        for signum in _ENDING_SIGNALS:
            if signal.getsignal(signum) is not signal.SIG_IGN:
                previous[signum] = signal.signal(signum, _raise_signalled)
    try:
        yield
    finally:
        for restored, handler in previous.items():
            signal.signal(restored, handler)


@contextlib.contextmanager
def _held_while_starting() -> Iterator[None]:
    """Hold Ctrl-C, SIGTERM and SIGHUP until ``Popen`` has returned.

    Between the child's start and ``Popen`` handing it back, a handled signal
    would raise (or end this process) with no process to stop, and the group
    would keep running in its own session (#10460). Each one that arrives is
    recorded instead, and raised again once the block ends, to whatever handler
    is in place then. A signal the caller ignores stays ignored. Off the main
    thread this does nothing, as :func:`_ending_signals_raise` does nothing.
    """
    arrived: list[int] = []

    def hold(signum: int, _frame: FrameType | None) -> None:
        arrived.append(signum)

    previous: dict[signal.Signals, _Handler] = {}
    if threading.current_thread() is threading.main_thread():
        for signum in _HELD_DURING_START:
            if signal.getsignal(signum) not in (signal.SIG_IGN, None):
                previous[signum] = signal.signal(signum, hold)
    try:
        yield
    finally:
        # Ctrl-C is restored last and raised last: a SIGTERM / SIGHUP held
        # behind it must not be dropped by the KeyboardInterrupt leaving this
        # block first, and the ending signals ask for the stronger outcome.
        for restored, handler in reversed(previous.items()):
            signal.signal(restored, handler)
        for held in sorted(set(arrived), key=lambda signum: signum == signal.SIGINT):
            signal.raise_signal(held)


def _group_alive(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # macOS answers EPERM for a group whose only members are zombies of
        # another parent; nothing in it can run, which is what is asked here.
        return False
    return True


def reap_leader(process: subprocess.Popen[Any], *, block: bool) -> bool:
    """Reap the leader with ``os.waitpid``, never through ``Popen``'s own lock.

    ``Popen.wait`` and ``poll`` take ``_waitpid_lock``. A Ctrl-C or SIGTERM whose
    handler runs just after ``_wait`` acquired it and before its ``try`` leaves
    it held for good: ``poll`` then answers ``None`` for ever and ``wait()``
    blocks on a lock nothing releases, so the caller never exits (#11211). Setting the public
    ``returncode`` makes any later ``wait`` / ``poll`` return at once. Shared by every
    script that ends a child after a raising signal handler (``agent_wait.py``,
    ``mutant_run.py``); ``tests/test_agent_wait_reaps_without_the_popen_lock_11214.py``
    refuses a bare ``.wait()`` anywhere under ``scripts/`` (#11214).
    """
    if process.returncode is not None:
        return True
    try:
        pid, status = os.waitpid(process.pid, 0 if block else os.WNOHANG)
    except ChildProcessError:
        process.returncode = 0  # reaped elsewhere; ``Popen`` records 0 as well
        return True
    if pid == 0:
        return False
    process.returncode = os.waitstatus_to_exitcode(status)
    return True


def stop_group(process: subprocess.Popen[Any]) -> None:
    """Stop the group ``process`` leads (it was started with a new session).

    The pid of a session leader is its group id, so no lookup is needed and no
    other group can be named by mistake.
    """
    pgid = process.pid
    try:
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(pgid, signal.SIGTERM)
        deadline = time.monotonic() + GROUP_STOP_GRACE_SECONDS
        while time.monotonic() < deadline:
            # Reaping the leader matters: an unreaped one keeps its group "alive".
            if reap_leader(process, block=False) and not _group_alive(pgid):
                break
            time.sleep(0.02)
    finally:
        # In ``finally`` so a second Ctrl-C or SIGTERM, which ends the grace
        # loop with an exception, still kills and reaps the group.
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(pgid, signal.SIGKILL)
        reap_leader(process, block=True)
        # Closed, not drained: a descendant that left the group can hold a pipe
        # open for ever, and reading it would put back the hang this removes.
        for stream in (process.stdout, process.stderr):
            if stream is not None:
                stream.close()


def _start_watcher(pgid: int) -> subprocess.Popen[bytes]:
    """Start the process that stops group ``pgid`` once this process is gone."""
    return subprocess.Popen(  # noqa: S603  # this interpreter running the literal _WATCHER with the group id and grace as numbers
        [
            sys.executable,
            "-I",
            "-c",
            _WATCHER,
            str(pgid),
            str(GROUP_STOP_GRACE_SECONDS),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def _end_watcher(watcher: subprocess.Popen[bytes]) -> None:
    """Kill and reap the watcher, then close its pipe, in that order.

    Closing first would hand it an end of input and have it signal the group id
    of a command that has finished. The reap does not go through ``Popen``'s
    lock (see :func:`reap_leader`).
    """
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.kill(watcher.pid, signal.SIGKILL)
    reap_leader(watcher, block=True)
    if watcher.stdin is not None:
        with contextlib.suppress(OSError):
            watcher.stdin.close()


def run_bounded(
    argv: Sequence[str],
    *,
    timeout: float,
    capture_output: bool = False,
    check: bool = False,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """``subprocess.run(argv, text=True, timeout=timeout)``, ending the group.

    ``timeout`` is required, with no default. Raises ``subprocess.TimeoutExpired``
    when it passes — after the group has been stopped — and
    ``CalledProcessError`` under ``check``, as ``subprocess.run`` does. The
    command reads ``/dev/null``: in its own session it has no terminal to read.
    """
    pipe = subprocess.PIPE if capture_output else None
    process: subprocess.Popen[str] | None = None
    watcher: subprocess.Popen[bytes] | None = None
    try:
        # The stop runs with the handlers still installed: a second SIGTERM
        # during the grace must raise there, not end this process by default.
        with _ending_signals_raise():
            try:
                with _held_while_starting():
                    process = subprocess.Popen(  # noqa: S603  # non-shell argv handed over by the caller, whose own justification covers its elements; this function adds none
                        list(argv),
                        cwd=cwd,
                        env=env,
                        stdin=subprocess.DEVNULL,
                        stdout=pipe,
                        stderr=pipe,
                        text=True,
                        start_new_session=True,
                    )
                    watcher = _start_watcher(process.pid)
                stdout, stderr = process.communicate(timeout=timeout)
            except BaseException:
                if process is not None:
                    stop_group(process)
                raise
            finally:
                if watcher is not None:
                    _end_watcher(watcher)
    except _Signalled as signalled:
        # Handed back to whatever the caller had for it, now restored: by
        # default that ends this process, as the signal was meant to.
        os.kill(os.getpid(), signalled.signum)
        raise SystemExit(128 + signalled.signum) from None
    completed = subprocess.CompletedProcess(
        list(argv), process.returncode, stdout, stderr
    )
    if check:
        completed.check_returncode()
    return completed


def run_bounded_status(
    argv: Sequence[str],
    *,
    timeout: float,
    capture_output: bool = False,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """:func:`run_bounded` for a caller that already handles a nonzero status.

    A limit that passes comes back as status :data:`EXPIRED_STATUS` with the
    reason on ``stderr``, so the caller's existing failure path reports it.
    """
    try:
        return run_bounded(
            argv, timeout=timeout, capture_output=capture_output, cwd=cwd, env=env
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            list(argv),
            EXPIRED_STATUS,
            stdout="",
            stderr=(
                f"`{' '.join(argv[:3])}` did not finish within {timeout:g}s; it "
                "and the processes it started were stopped (#10290)"
            ),
        )
