from __future__ import annotations

import os
import shutil
import tempfile
import zlib

import pytest

import ci_shard_split
import templates_memo
import worker_peak
from xdist_groups import group_for


def pytest_configure(config):
    """A CI shard's share of a split file (#348); a conftest cannot name plugins here.

    Also the run's one retail measurement (gen#536): the controller makes a directory and names it
    in the environment before it starts the xdist workers, so ``retail_figures.figures()`` measures
    once for the run, not once per worker. A worker inherits the name and never makes its own.
    """
    config.pluginmanager.register(ci_shard_split, "ci_shard_split")
    config.pluginmanager.register(worker_peak, "worker_peak")
    templates_memo.watch()
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
    from synthetic_ecommerce_data.domains.retail import retail_figures  # noqa: PLC0415

    return retail_figures.figures()


def pytest_addoption(parser):
    parser.addoption(
        "--order-seed", type=int, default=None, metavar="N",
        help="run the tests in an order shuffled from N; off by default (#1107)",
    )  # fmt: skip


def pytest_report_header(config):
    seed = config.getoption("order_seed", None)
    return None if seed is None else f"test order: shuffled by --order-seed={seed}"


def _shuffled(items, seed):
    """Modules, then classes, then tests, each placed by a hash of the seed and its name (#1107).

    A module (and a class) stays together, so its fixtures are built once; the hash, not a
    shared generator, keeps one order on every xdist worker and every CI shard.
    """

    def key(item):
        file = item.nodeid.split("::")[0]
        cls = f"{file}::{getattr(getattr(item, 'cls', None), '__qualname__', '')}"
        return [(zlib.crc32(f"{seed}::{name}".encode()), name) for name in (file, cls, item.nodeid)]

    return sorted(items, key=key)


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    """Shuffle from ``--order-seed``, then keep a module's tests on one worker (#348).

    ``tryfirst``: xdist's worker-side hook (``xdist/remote.py``) suffixes each node id with
    ``@<group>`` from the markers it sees, and it runs before a plain conftest hook, so without
    this the mark was added too late and a module's tests spread over the workers (#442). The
    shuffle comes first too, as pytest-randomly's did, so ``ci_shard_split`` deals a split file
    out in the shuffled order: the same in every shard, so each test still runs in one. A child
    conftest may import this hook without the option (``tests/test_xdist_group_honoured_442.py``).
    """
    seed = config.getoption("order_seed", None)
    if seed is not None:
        items[:] = _shuffled(items, seed)
    for item in items:
        module = getattr(item, "module", None)
        group = group_for(module) if module is not None else None
        if group is not None:
            item.add_marker(pytest.mark.xdist_group(group))


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """The retail templates are computed once per worker (#1035)."""
    templates_memo.install()
