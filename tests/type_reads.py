"""Which test files read a type table, and the guard of the files listed as reading none (#1035).

``scripts/ci_type_free.json`` lists test files that read no table filled by the type modules of
the industrial domain (:class:`...core.typespec.RegistryTable`), so ``scripts/ci_select.py`` does
not select them for a change to a type module. A run proves or breaks that: this plugin
(``tests/conftest.py`` registers it) notes each call of the functions a read goes through
(:data:`READERS`) against the test file that was collected or run, and a listed file that made
one fails. ``TYPE_READS_OUT`` names a file for what the run saw, which
``scripts/ci_type_free.py --refresh`` reads.

``sys.monitoring`` sees the call itself, so a read counts whether or not an earlier file of the
worker already loaded the types. It does not see another process: a file that starts one is never
listed (``scripts/ci_type_free.py``). A read while a product module is imported counts only for the
file that imported it first, so ``tests/test_type_free_1035.py`` refuses such a read.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

#: file suffix -> the functions of it a read of a type table goes through. A name that is not
#: here is a lazy table the package hands core without loading a type (``_figures``: core's own
#: import asks for it, and the table it hands over is read through ``ensure_registered``).
READERS: dict[str, frozenset[str]] = {
    "/core/typespec.py": frozenset({"ensure_registered", "registered", "discover", "modelled"}),
    "/domains/industrial/__init__.py": frozenset(
        {"_product_types", "_brand_families", "_pack_types", "_orientations", "_load_types"}
    ),
}
TABLE_ENV = "TYPE_FREE_FILE"
OUT_ENV = "TYPE_READS_OUT"
TABLE = Path(__file__).resolve().parent.parent / "scripts" / "ci_type_free.json"

_TOOL = 4
_state: dict = {"file": None, "ran": set(), "read": set(), "told": set()}


def _is_reader(code) -> bool:
    return any(
        code.co_name in names and code.co_filename.endswith(suffix)
        for suffix, names in READERS.items()
    )


def _called(code, _offset):
    if not _is_reader(code):
        return sys.monitoring.DISABLE
    if _state["file"] is not None:
        _state["read"].add(_state["file"])
    return None


def watch() -> None:
    """Note the readers' calls from here on; a Python with no ``sys.monitoring`` notes nothing."""
    monitoring = getattr(sys, "monitoring", None)
    if monitoring is None or monitoring.get_tool(_TOOL) is not None:
        return
    monitoring.use_tool_id(_TOOL, "type_reads")
    monitoring.register_callback(_TOOL, monitoring.events.PY_START, _called)
    monitoring.set_events(_TOOL, monitoring.events.PY_START)


def listed() -> frozenset[str]:
    path = Path(os.environ.get(TABLE_ENV) or TABLE)
    return frozenset(json.loads(path.read_text(encoding="utf-8")))


def pytest_configure(config) -> None:
    config._type_free = listed()
    watch()


@pytest.hookimpl(hookwrapper=True)
def pytest_make_collect_report(collector):
    if isinstance(collector, pytest.Module):
        _state["file"] = collector.nodeid.split("::")[0]
        yield
        _state["file"] = None
    else:
        yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item):
    _state["file"] = item.nodeid.split("::")[0]
    _state["ran"].add(_state["file"])
    yield
    _state["file"] = None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_teardown(item):
    yield
    file = item.nodeid.split("::")[0]
    if file in item.config._type_free and file in _state["read"] and file not in _state["told"]:
        _state["told"].add(file)
        pytest.fail(
            f"{file} is listed in scripts/ci_type_free.json as reading no type table, and it read "
            "one (at or before this test): a change to a type module must select it. Remove its "
            "line there (docs/ci-sharding.md, 'A change to an industrial type').",
            pytrace=False,
        )


def pytest_sessionfinish(session) -> None:
    output = getattr(session.config, "workeroutput", None)
    if output is not None:
        output["type_reads"] = {"ran": sorted(_state["ran"]), "read": sorted(_state["read"])}


@pytest.hookimpl(optionalhook=True)
def pytest_testnodedown(node, error) -> None:  # noqa: ARG001 - xdist's hook signature
    for key, files in (getattr(node, "workeroutput", {}).get("type_reads") or {}).items():
        _state[key].update(files)


def pytest_terminal_summary(terminalreporter, config) -> None:  # noqa: ARG001
    out = os.environ.get(OUT_ENV)
    if out:
        seen = {key: sorted(_state[key]) for key in ("ran", "read")}
        Path(out).write_text(json.dumps(seen, indent=1) + "\n", encoding="utf-8")
