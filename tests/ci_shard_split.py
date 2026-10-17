"""Run only this CI shard's share of a split test file (#348); a plugin that is inert off CI.

``tests/conftest.py`` loads it (``pytest_plugins``). The workflow's tests step sets
``CI_SHARD`` and ``CI_SHARDS``; a file in ``scripts/ci_shards.py``'s ``SPLIT_FILES`` is
listed in every shard, and its tests, in collection order, are dealt out by position
(``ci_shards.keeps``), so each test id runs in exactly one shard. With either variable
unset, not a number, or ``CI_SHARDS`` 1 (the local run), every test is kept.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent


def _ci_shards():
    """scripts/ci_shards.py, loaded by path (``scripts`` is not a package)."""
    if "ci_shards" not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            "ci_shards", _REPO / "scripts" / "ci_shards.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules["ci_shards"] = module
        spec.loader.exec_module(module)
    return sys.modules["ci_shards"]


def pytest_collection_modifyitems(config, items):
    shard, shards = os.environ.get("CI_SHARD", ""), os.environ.get("CI_SHARDS", "")
    if not (shard.isdigit() and shards.isdigit() and int(shards) > 1):
        return
    ci_shards = _ci_shards()
    position: dict[str, int] = {}
    kept, dropped = [], []
    for item in items:
        name = Path(str(item.path)).resolve().relative_to(_REPO).as_posix()
        if name in ci_shards.SPLIT_FILES:
            index = position.get(name, 0)
            position[name] = index + 1
            if not ci_shards.keeps(index, int(shard), int(shards)):
                dropped.append(item)
                continue
        kept.append(item)
    if dropped:
        config.hook.pytest_deselected(items=dropped)
        items[:] = kept
