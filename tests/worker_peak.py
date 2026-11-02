"""Each xdist worker's peak memory, printed at the end of the run (#539).

A worker reports ``VmHWM`` as it finishes and the controller prints one ``peak worker memory:``
line, so a CI shard's log shows the figure the suite's memory work is judged by. ``VmHWM`` and not
``ru_maxrss``: the latter survives ``exec``, so a worker started from a large process reports that
process's peak. A run with no workers prints nothing. ``tests/conftest.py`` registers this.

Each test module's peak too (#790): a worker sets its high-water mark back to what it holds now
(``5`` to ``/proc/self/clear_refs``) before each module, so the mark after the module's last test
is the worker's peak while that module ran (what earlier modules left resident counts too). The
``module peak memory:`` line names the modules over :data:`HEAVY_MB`, so a shard's log says which
modules need a worker of their own. A worker that cannot reset the mark (no ``/proc``) reports no
module.
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


#: A module whose peak is over this many MB is named in the ``module peak memory:`` line.
HEAVY_MB = 1500


def reset_peak() -> bool:
    """Set this process's high-water mark back to its resident memory now (Linux only)."""
    try:
        Path("/proc/self/clear_refs").write_text("5", encoding="ascii")
    except OSError:
        return False
    return True


def module_summary(peaks: dict[str, int]) -> str:
    """The line the run prints for its modules: how many, then each one over HEAVY_MB."""
    heavy = sorted(((mb, m) for m, mb in peaks.items() if mb > HEAVY_MB), reverse=True)
    each = ", ".join(f"{m} {mb}" for mb, m in heavy) or "none"
    return f"module peak memory: {len(heavy)} of {len(peaks)} modules over {HEAVY_MB} MB: {each}"


def _module(item: pytest.Item) -> str:
    return item.nodeid.split("::", 1)[0]


@pytest.hookimpl(wrapper=True)
def pytest_runtest_protocol(item: pytest.Item, nextitem: pytest.Item | None):
    config = item.config
    if not hasattr(config, "workerinput"):
        return (yield)
    peaks = config.__dict__.setdefault("_module_peaks", {})
    if getattr(config, "_peak_module", None) != _module(item):
        config._peak_module = _module(item) if reset_peak() else None
    result = yield
    # the module's fixtures are torn down in its last test's teardown, inside this protocol
    module, mb = config._peak_module, own_peak_mb()
    if module is not None and mb is not None:
        peaks[module] = max(peaks.get(module, 0), mb)
    return result


def pytest_sessionfinish(session: pytest.Session) -> None:
    if hasattr(session.config, "workerinput"):
        session.config.workeroutput["peak_mb"] = own_peak_mb()
        session.config.workeroutput["module_peaks"] = session.config.__dict__.get(
            "_module_peaks", {}
        )


@pytest.hookimpl(optionalhook=True)
def pytest_testnodedown(node, error) -> None:  # noqa: ARG001 - xdist's hook signature
    output = getattr(node, "workeroutput", {})
    peak = output.get("peak_mb")
    if peak is not None:
        node.config.__dict__.setdefault("_worker_peaks", {})[node.gateway.id] = peak
    modules = node.config.__dict__.setdefault("_all_module_peaks", {})
    for module, mb in (output.get("module_peaks") or {}).items():
        modules[module] = max(modules.get(module, 0), mb)


def pytest_terminal_summary(terminalreporter, config) -> None:
    peaks = getattr(config, "_worker_peaks", None)
    if peaks:
        terminalreporter.write_line(summary(peaks))
    modules = getattr(config, "_all_module_peaks", None)
    if modules:
        terminalreporter.write_line(module_summary(modules))
