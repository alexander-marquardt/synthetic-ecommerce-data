from __future__ import annotations

import os
import shutil
import struct
import sys
import tempfile
from pathlib import Path

import pytest

import ci_shard_split
from xdist_groups import group_for

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"


def pytest_configure(config):
    """A CI shard's share of a split file (#348); a conftest cannot name plugins here.

    Also the run's one retail measurement (gen#536): the controller makes a directory and names it
    in the environment before it starts the xdist workers, so ``retail_figures.figures()`` measures
    once for the run, not once per worker. A worker inherits the name and never makes its own.
    """
    config.pluginmanager.register(ci_shard_split, "ci_shard_split")
    if hasattr(config, "workerinput") or "RETAIL_FIGURES_CACHE" in os.environ:
        return
    config._retail_figures_cache = tempfile.mkdtemp(prefix="retail-figures-")
    os.environ["RETAIL_FIGURES_CACHE"] = config._retail_figures_cache


def pytest_unconfigure(config):
    made = getattr(config, "_retail_figures_cache", None)
    if made:
        os.environ.pop("RETAIL_FIGURES_CACHE", None)
        shutil.rmtree(made, ignore_errors=True)


@pytest.fixture(scope="session")
def retail_figures_measured() -> dict:
    """The retail build's measured totals for this tree, measured once for the run (gen#536)."""
    if str(RETAIL) not in sys.path:
        sys.path.insert(0, str(RETAIL))
    import retail_figures  # noqa: PLC0415 -- the prototype's own directory is its import root

    return retail_figures.figures()


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    """Keep a module's tests on one worker under ``--dist loadgroup`` (#348); inert otherwise.

    ``tryfirst``: xdist's worker-side hook (``xdist/remote.py``) suffixes each node id with
    ``@<group>`` from the markers it sees, and it runs before a plain conftest hook, so without
    this the mark was added too late and a module's tests spread over the workers (#442).
    """
    for item in items:
        module = getattr(item, "module", None)
        group = group_for(module) if module is not None else None
        if group is not None:
            item.add_marker(pytest.mark.xdist_group(group))


@pytest.fixture
def png_size():
    """Width and height read out of the PNG's own IHDR chunk.

    Deliberately independent of the production helper and of the figure size:
    the question is what the file says, not what the renderer intended.
    """

    def _read(path: Path) -> tuple[int, int]:
        raw = Path(path).read_bytes()
        assert raw[:8] == b"\x89PNG\r\n\x1a\n", f"{path} is not a PNG"
        assert raw[12:16] == b"IHDR", f"{path} has no IHDR where one must be"
        return struct.unpack(">II", raw[16:24])

    return _read
