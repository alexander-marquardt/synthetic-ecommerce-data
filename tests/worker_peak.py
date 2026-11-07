"""Each xdist worker's peak memory, printed at the end of the run (#539).

A worker reports ``VmHWM`` as it finishes and the controller prints one ``peak worker memory:``
line, so a CI shard's log shows the figure the suite's memory work is judged by. ``VmHWM`` and not
``ru_maxrss``: the latter survives ``exec``, so a worker started from a large process reports that
process's peak. A run with no workers prints nothing. ``tests/conftest.py`` registers this.

Each test module's peak too (#790): a worker sets its high-water mark back to what it holds now
(``5`` to ``/proc/self/clear_refs``) before each module, so the mark after the module's last test
is the worker's peak while that module ran (what earlier modules left resident counts too). The
``module peak memory:`` line names the modules over :data:`HEAVY_MB`, so a shard's log says which
modules need a worker of their own, and ``MODULE_PEAKS_OUT`` names a file for every module's
figure, which picks a shard's worker count (``scripts/ci_shards.py --workers``). A worker that
cannot reset the mark (no ``/proc``) reports no
module. Before each reset the worker keeps the mark it clears, so its ``peak worker memory:``
figure is its peak over the whole run, not the last module's (#869).

A killed worker sends no ``workeroutput`` (#845), so when the run names a directory in
:data:`PEAK_DIR_ENV` each worker also appends to ``<dir>/<worker id>.peaks``, flushed as it goes: a
``<module>\t<MB>`` line as a module starts and again each time its peak rises. A worker the OOM
killer ends leaves its finished modules' peaks, and its last line names the module it died in.
``scripts/ci_run_pytest.py`` names the directory and prints that last line for a lost worker.
"""

from __future__ import annotations

import json
import os
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


#: The directory a worker appends its module peaks to, one file per worker (#845); unset, none.
PEAK_DIR_ENV = "WORKER_PEAK_DIR"
#: The file the controller writes every module's peak to, as ``{module: MB}`` JSON (#790): a CI
#: shard uploads it, and ``scripts/ci_shards.py --refresh-peaks`` reads it. Unset, none.
MODULE_PEAKS_OUT_ENV = "MODULE_PEAKS_OUT"


def _module(item: pytest.Item) -> str:
    return item.nodeid.split("::", 1)[0]


def _record(config: pytest.Config, module: str, mb: int) -> None:
    """Append ``module``'s peak to this worker's file, so a kill after this line keeps it."""
    folder = os.environ.get(PEAK_DIR_ENV)
    if folder:
        path = Path(folder) / f"{config.workerinput['workerid']}.peaks"
        with path.open("a", encoding="utf-8") as out:
            out.write(f"{module}\t{mb}\n")


def _session_peak(config: pytest.Config) -> int | None:
    """This worker's peak over its run so far: the mark now, or a higher one a reset cleared."""
    now = own_peak_mb()
    if now is None:
        return None
    config._session_peak = max(getattr(config, "_session_peak", 0), now)
    return config._session_peak


@pytest.hookimpl(wrapper=True)
def pytest_runtest_protocol(item: pytest.Item, nextitem: pytest.Item | None):
    config = item.config
    if not hasattr(config, "workerinput"):
        return (yield)
    peaks = config.__dict__.setdefault("_module_peaks", {})
    if getattr(config, "_peak_module", None) != _module(item):
        _session_peak(config)  # before the reset clears the mark
        config._peak_module = _module(item) if reset_peak() else None
        start = own_peak_mb()
        if config._peak_module is not None and start is not None:
            _record(config, config._peak_module, start)
    result = yield
    # the module's fixtures are torn down in its last test's teardown, inside this protocol
    module, mb = config._peak_module, own_peak_mb()
    if module is not None and mb is not None:
        if mb > peaks.get(module, 0):
            _record(config, module, mb)
        peaks[module] = max(peaks.get(module, 0), mb)
    return result


def pytest_sessionfinish(session: pytest.Session) -> None:
    if hasattr(session.config, "workerinput"):
        session.config.workeroutput["peak_mb"] = _session_peak(session.config)
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
        out = os.environ.get(MODULE_PEAKS_OUT_ENV)
        if out:
            table = json.dumps(dict(sorted(modules.items())), indent=1)
            Path(out).write_text(table + "\n", encoding="utf-8")
