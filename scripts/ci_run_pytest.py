#!/usr/bin/env python3
"""Run a CI shard's pytest command; a lost xdist worker is an infra failure, rerun once (#629).

    ci_run_pytest.py [--reruns N] -- <pytest command...>

Three pull requests had a ``tests`` shard end red with no test id: both xdist workers went down
within a tenth of a second (``node down: Not properly terminated``), the controller then raised
``INTERNALERROR> KeyError: <WorkerController gw2>`` replacing them, and the verdict read as a test
failure. Main's same shard was green. The runner's kernel log, which a job cannot read, named the
cause: the job container's 6 GiB memory cap killed both workers (docs/ci-sharding.md, #629).

This runs the command, passing its output through. When the output shows a lost worker it
prints ``infra: worker lost`` with what a job can read about memory (``evidence``), and runs the
command again, ``--reruns`` times (default 1). A run that loses a worker on every attempt ends
with ``EXIT_INFRA``, not a test's exit code. A run whose tests failed with every worker alive is
never rerun: a failing test stays a failing test, and the command's own exit code is the result.

Each attempt names a fresh directory in ``WORKER_PEAK_DIR``, where ``tests/worker_peak.py`` has
each worker append its module peaks as it runs (#845). For each worker the log shows went down,
it prints ``<gw> was in <module> at <MB> MB``: the last line that worker wrote before the kill.
"""

from __future__ import annotations

import argparse
import os
import re
import resource
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

#: Exit code of a run that lost a worker on every attempt (EX_TEMPFAIL): not a test's code.
EXIT_INFRA = 75

#: What xdist and pytest print when workers die, from the logs of the three red runs.
#: Anchored to what xdist prints, so a traceback, an ``E`` line or a quoted repr that carries the
#: same words (a test that parses these logs) is not read as a lost worker.
LOST_SIGNATURES = (
    re.compile(r"^[.sxXFE]*\[gw\d+\] node down: Not properly terminated\s*$", re.MULTILINE),
    re.compile(r"^INTERNALERROR> KeyError: <WorkerController ", re.MULTILINE),
)
CRASHED_TEST = re.compile(r"worker '(gw\d+)' crashed while running '([^']+)'")
NODE_DOWN = re.compile(r"^[.sxXFE]*\[(gw\d+)\] node down: Not properly terminated\s*$")
MB = 1024 * 1024
#: Where ``tests/worker_peak.py`` appends each worker's module peaks (#845).
PEAK_DIR_ENV = "WORKER_PEAK_DIR"


def worker_lost(text: str) -> bool:
    """Whether ``text`` (a line or a whole log) shows an xdist worker that went down."""
    return any(sig.search(text) for sig in LOST_SIGNATURES)


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return None


def _mb(value: str | None) -> str:
    return f"{int(value) // MB} MB" if value and value.isdigit() else (value or "unreadable")


def _meminfo_mb(field: str) -> str:
    text = _read(Path("/proc/meminfo")) or ""
    match = re.search(rf"^{field}:\s+(\d+) kB", text, re.MULTILINE)
    return f"{int(match.group(1)) // 1024} MB" if match else "unreadable"


def evidence(cgroup: Path = Path("/sys/fs/cgroup")) -> list[str]:
    """What the job can read about memory: the cgroup's OOM count and peak, the host's headroom."""
    lines = []
    events = _read(cgroup / "memory.events")
    peak, limit = _read(cgroup / "memory.peak"), _read(cgroup / "memory.max")
    if events is None and peak is None and limit is None:
        lines.append(f"no cgroup memory files under {cgroup}")
    else:
        counts = dict(ln.split() for ln in (events or "").splitlines() if len(ln.split()) == 2)
        lines.append(
            f"cgroup: oom={counts.get('oom', '?')} oom_kill={counts.get('oom_kill', '?')} "
            f"peak={_mb(peak)} limit={_mb(limit)}"
        )
    rss_kb = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    rss_mb = rss_kb // 1024 if sys.platform != "darwin" else rss_kb // MB
    lines.append(
        f"largest process so far: {rss_mb} MB; host MemAvailable={_meminfo_mb('MemAvailable')} "
        f"SwapFree={_meminfo_mb('SwapFree')}"
    )
    return lines


def _kernel_oom_lines() -> list[str]:
    """Kernel OOM lines, when the job may read the kernel log (a container usually may not)."""
    try:
        done = subprocess.run(["dmesg"], capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.SubprocessError):
        return ["dmesg: not readable here"]
    if done.returncode != 0:
        return ["dmesg: not readable here"]
    oom = re.compile(r"out of memory|oom-kill|Killed process", re.IGNORECASE)
    hits = [ln for ln in done.stdout.splitlines() if oom.search(ln)]
    return hits[-5:] or ["dmesg: readable, no OOM line"]


def last_module(peaks: Path, worker: str) -> str:
    """Where ``worker`` was when it went down, from the last line of its peak file (#845)."""
    lines = (_read(peaks / f"{worker}.peaks") or "").splitlines()
    module, _, mb = lines[-1].rpartition("\t") if lines else ("", "", "")
    if not module or not mb.isdigit():
        return f"{worker} left no module peak (no /proc, or killed before its first module)"
    return f"{worker} was in {module} at {mb} MB"


def run_once(command: list[str], peaks: Path) -> tuple[int, bool, list[str]]:
    """Run ``command`` passing its output through: exit code, a worker was lost, what it names.

    The names are each crashed test, then where each worker that went down was (#845).
    """
    lost, crashed, down = False, [], []
    env = os.environ | {PEAK_DIR_ENV: str(peaks)}
    with subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace",
        env=env,
    ) as child:  # fmt: skip
        assert child.stdout is not None
        for line in child.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            lost = lost or worker_lost(line)
            found = CRASHED_TEST.search(line)
            if found:
                crashed.append(f"{found.group(1)} crashed while running {found.group(2)}")
            gone = NODE_DOWN.search(line)
            if gone and gone.group(1) not in down:
                down.append(gone.group(1))
    return child.returncode, lost, crashed + [last_module(peaks, w) for w in down]


def main(argv: list[str]) -> int:
    split = argv.index("--") if "--" in argv else len(argv)
    head, command = argv[:split], argv[split + 1 :]
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--reruns", type=int, default=1, help="extra attempts after a lost worker")
    args = parser.parse_args(head)
    if not command:
        parser.error("no command after --")
    attempt = 0
    while True:
        attempt += 1
        peaks = Path(tempfile.mkdtemp(prefix="worker-peaks-"))
        try:
            code, lost, crashed = run_once(command, peaks)
        finally:
            shutil.rmtree(peaks, ignore_errors=True)
        if not lost:
            return code
        for line in evidence():
            print(f"ci_run_pytest: attempt {attempt}: {line}", flush=True)
        total = args.reruns + 1
        print(f"::warning::infra: worker lost on attempt {attempt} of {total}", flush=True)
        for line in [*crashed, *_kernel_oom_lines()]:
            print(f"ci_run_pytest: {line}", flush=True)
        if attempt > args.reruns:
            print(
                f"::error::infra: worker lost on all {attempt} attempts: this is the runner, or a "
                "test that kills its worker; it is not a failing assertion",
                flush=True,
            )
            return EXIT_INFRA
        print("infra: worker lost; running the shard once more", flush=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
