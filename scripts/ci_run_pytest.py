#!/usr/bin/env python3
"""Run a CI shard's pytest command; a lost xdist worker is an infra failure, rerun once (#629).

    ci_run_pytest.py [--reruns N] -- <pytest command...>

Three pull requests had a ``tests`` shard end red with no test id: both xdist workers went down
within a tenth of a second (``node down: Not properly terminated``), the controller then raised
``INTERNALERROR> KeyError: <WorkerController gw2>`` replacing them, and the verdict read as a test
failure. Main's same shard was green. The runner's kernel log is not readable from a job, so the
cause (an out-of-memory kill is the first hypothesis) was never shown.

This runs the command, passing its output through. When the output shows a lost worker it
prints ``infra: worker lost`` with what a job can read about memory (``evidence``), and runs the
command again, ``--reruns`` times (default 1). A run that loses a worker on every attempt ends
with ``EXIT_INFRA``, not a test's exit code. A run whose tests failed with every worker alive is
never rerun: a failing test stays a failing test, and the command's own exit code is the result.
"""

from __future__ import annotations

import argparse
import re
import resource
import subprocess
import sys
from pathlib import Path

#: Exit code of a run that lost a worker on every attempt (EX_TEMPFAIL): not a test's code.
EXIT_INFRA = 75

#: What xdist and pytest print when workers die, from the logs of the three red runs.
LOST_SIGNATURES = (
    re.compile(r"node down: Not properly terminated"),
    re.compile(r"INTERNALERROR> KeyError: <WorkerController "),
)
CRASHED_TEST = re.compile(r"worker '(gw\d+)' crashed while running '([^']+)'")
MB = 1024 * 1024


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


def run_once(command: list[str]) -> tuple[int, bool, list[str]]:
    """Run ``command`` passing its output through: exit code, a worker was lost, crashed tests."""
    lost, crashed = False, []
    with subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace"
    ) as child:
        assert child.stdout is not None
        for line in child.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            lost = lost or worker_lost(line)
            found = CRASHED_TEST.search(line)
            if found:
                crashed.append(f"{found.group(1)} crashed while running {found.group(2)}")
    return child.returncode, lost, crashed


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
        code, lost, crashed = run_once(command)
        for line in evidence():
            print(f"ci_run_pytest: attempt {attempt}: {line}", flush=True)
        if not lost:
            return code
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
