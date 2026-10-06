"""The type seam: one module per product type, found by discovery (#48, #27).

STUB. The red commit pins the contract in ``tests/test_type_seam.py``; the
implementation follows in the next commit.
"""

from __future__ import annotations

import random
from collections.abc import Mapping

#: The package type modules are discovered under: one directory per family,
#: one module per type, each exposing ``SPEC``.
TYPES_PACKAGE = "synthetic_industrial_products.product_types"


class TypeModuleError(ImportError):
    """A type module that cannot be imported, named by its dotted path."""


class TypeCollisionError(ValueError):
    """Two types that derive the same part-number block or id."""


def discover(package: str = TYPES_PACKAGE) -> dict[str, object]:
    return {}


def part_number_block(type_key: str) -> int:
    return 0


def block_of(type_key: str) -> int:
    return 0


def check_collisions(blocks: Mapping[str, int]) -> None:
    return None


def type_rng(seed: int, type_key: str) -> random.Random:
    return random.Random(f"{seed}:{type_key}")
