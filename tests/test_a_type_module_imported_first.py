"""A type module, or discovery, as a fresh process's first import (#54).

A builder who tests their own module writes
``from ...product_types.<family>.<key> import SPEC`` as the first project
import. Each case does exactly that in a fresh interpreter, then reads the
type from a shared table. A breadth module imports ``breadth`` for
``BreadthRow``, so anything ``breadth`` does at import runs while the type
module is still half-initialised.
"""

from __future__ import annotations

import pkgutil
import subprocess
import sys

import pytest

import synthetic_ecommerce_data.domains.industrial.product_types as types_pkg

_MODULES = sorted(
    found.name
    for found in pkgutil.walk_packages(types_pkg.__path__, prefix=f"{types_pkg.__name__}.")
    if not found.ispkg
)

_SCRIPT = """
import importlib, sys
module = importlib.import_module(sys.argv[1])
from synthetic_ecommerce_data.domains.industrial.taxonomy import LEAVES
LEAVES[module.SPEC.key]
"""


@pytest.mark.parametrize("module", _MODULES)
def test_a_type_module_imported_first_still_registers(module: str) -> None:
    result = subprocess.run(
        [sys.executable, "-c", _SCRIPT, module], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr[-600:]


@pytest.mark.parametrize(
    "first_call", ["sorted(typespec.discover())", "typespec.block_of('shaft_collars')"]
)
def test_discover_called_first_finds_every_type_module(first_call: str) -> None:
    """``typespec.discover()`` or ``block_of`` as a fresh process's first call."""
    script = f"from synthetic_ecommerce_data.core import typespec\nprint({first_call})\n"
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr[-600:]
