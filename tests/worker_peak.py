"""Each xdist worker's peak memory, printed at the end of the run (#539).

A worker reports ``VmHWM`` as it finishes and the controller prints one ``peak worker memory:``
line, so a CI shard's log shows the figure the suite's memory work is judged by. ``VmHWM`` and not
``ru_maxrss``: the latter survives ``exec``, so a worker started from a large process reports that
process's peak. A run with no workers prints nothing. ``tests/conftest.py`` registers this.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_HIGH_WATER = re.compile(r"^VmHWM:\s+(\d+) kB$", re.MULTILINE)


def peak_mb(status: str) -> int | None:
    """The peak resident memory a ``/proc/<pid>/status`` text states, in MB."""
    match = _HIGH_WATER.search(status)
    return int(match.group(1)) // 1024 if match else None


def own_peak_mb() -> int | None:
    """This process's peak in MB, or None on a platform with no ``/proc`` (macOS)."""
    try:
        return peak_mb(Path("/proc/self/status").read_text(encoding="utf-8"))
    except OSError:
        return None


def summary(peaks: dict[str, int]) -> str:
    """The line the run prints: the largest worker, then each by name."""
    each = ", ".join(f"{name} {mb}" for name, mb in sorted(peaks.items()))
    return f"peak worker memory: {max(peaks.values())} MB ({each})"


def pytest_sessionfinish(session: pytest.Session) -> None:
    if hasattr(session.config, "workerinput"):
        session.config.workeroutput["peak_mb"] = own_peak_mb()


@pytest.hookimpl(optionalhook=True)
def pytest_testnodedown(node, error) -> None:  # noqa: ARG001 - xdist's hook signature
    peak = getattr(node, "workeroutput", {}).get("peak_mb")
    if peak is not None:
        node.config.__dict__.setdefault("_worker_peaks", {})[node.gateway.id] = peak


def pytest_terminal_summary(terminalreporter, config) -> None:
    peaks = getattr(config, "_worker_peaks", None)
    if peaks:
        terminalreporter.write_line(summary(peaks))
