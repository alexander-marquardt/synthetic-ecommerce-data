"""Review plant for #54: a type module imported before anything else.

A builder who tests their own module naturally writes
``from ...product_types.<family>.<key> import SPEC`` as the first project
import. Each case does exactly that in a fresh interpreter, then reads the
type from a shared table.
"""

from __future__ import annotations

import pkgutil
import subprocess
import sys

import pytest

import synthetic_industrial_products.product_types as types_pkg

_MODULES = sorted(
    found.name
    for found in pkgutil.walk_packages(types_pkg.__path__, prefix=f"{types_pkg.__name__}.")
    if not found.ispkg
)

_SCRIPT = """
import importlib, sys
module = importlib.import_module(sys.argv[1])
from synthetic_industrial_products.catalog.taxonomy import LEAVES
LEAVES[module.SPEC.key]
"""


@pytest.mark.parametrize("module", _MODULES)
def test_a_type_module_imported_first_still_registers(module: str) -> None:
    result = subprocess.run(
        [sys.executable, "-c", _SCRIPT, module], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr[-600:]


def test_discover_called_first_finds_every_type_module() -> None:
    """``typespec.discover()`` (or ``block_of``) as a fresh process's first call."""
    script = (
        "from synthetic_industrial_products.catalog import typespec\n"
        "print(sorted(typespec.discover()))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr[-600:]
