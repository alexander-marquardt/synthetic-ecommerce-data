"""The type seam: what makes one product type's output its own (#48, #27).

Several builders add types in parallel, so a type's SKUs, product ids and
drawn values must depend on nothing but the seed and that type's own key and
code. Three things here make that hold, each a pure function of the key:

* :func:`type_rng` -- the type's random stream. A stream shared by every type
  and walked in type order would make each type's draws depend on every type
  built before it.
* :func:`block_of` -- the type's four-digit part-number block, which leads
  every SKU and product id the type issues, so two types can never issue the
  same identifier and no global sequence is needed to keep them apart.
* :func:`discover` -- the per-type modules under :data:`TYPES_PACKAGE`, found
  by walking the package rather than by a hand-kept list that every new type
  would have to edit.

A derived block can land on another type's (about one chance in a hundred per
new type at today's count). :func:`check_collisions` refuses that build and
names both types; the fix is a ``part_number_block=`` on one type's own spec.
"""

from __future__ import annotations

import hashlib
import importlib
import pkgutil
import random
from collections.abc import Mapping
from dataclasses import dataclass, replace
from functools import cache

#: The package type modules are discovered under: one directory per family,
#: one module per type, each exposing ``SPEC``.
TYPES_PACKAGE = "synthetic_industrial_products.product_types"

#: Part-number blocks are four digits, so a block always prints the same width.
BLOCK_LOW = 1000
BLOCK_HIGH = 9999

#: The scrambled sequence after the block: six digits per type.
SEQUENCE_SPACE = 10**6

#: A stride coprime to 10**6, so consecutive products do not read as a counter.
_PART_STRIDE = 390_581


class TypeModuleError(ImportError):
    """A type module that cannot be imported, named by its dotted path."""


class TypeCollisionError(ValueError):
    """Two types that derive the same part-number block or id."""


@dataclass(frozen=True)
class TypeSpec:
    """What a type module declares about itself as ``SPEC``.

    ``part_number_block`` is only for the rare type whose derived block
    collides with another's; every other type leaves it unset.
    """

    key: str
    part_number_block: int | None = None
    #: The dotted module the spec was found in, filled in by :func:`discover`.
    module: str = ""


def discover(package: str = TYPES_PACKAGE) -> dict[str, TypeSpec]:
    """Every type module under ``package``, by type key.

    A module that fails to import is reported by its dotted path, because the
    underlying error (a typo in a table, a bad import) rarely says which of
    many type files it came from.
    """

    def refuse(name: str) -> None:
        raise TypeModuleError(f"type package {name} failed to import")

    try:
        root = importlib.import_module(package)
    except Exception as exc:  # noqa: BLE001 - re-raised, naming the package
        raise TypeModuleError(f"type package {package} failed to import: {exc!r}") from exc
    specs: dict[str, TypeSpec] = {}
    for found in pkgutil.walk_packages(root.__path__, prefix=f"{package}.", onerror=refuse):
        if found.ispkg:
            continue
        try:
            module = importlib.import_module(found.name)
        except Exception as exc:  # noqa: BLE001 - re-raised, naming the module
            raise TypeModuleError(f"type module {found.name} failed to import: {exc!r}") from exc
        spec = getattr(module, "SPEC", None)
        if not isinstance(spec, TypeSpec):
            raise TypeModuleError(f"type module {found.name} declares no SPEC = TypeSpec(...)")
        if found.name.rsplit(".", 1)[1] != spec.key:
            raise TypeModuleError(
                f"type module {found.name} declares {spec.key!r}; a type module is named "
                "after its type key, so the key can be found from the file and back"
            )
        if spec.key in specs:
            raise TypeCollisionError(
                f"type {spec.key!r} is declared by both {specs[spec.key].module} and {found.name}"
            )
        specs[spec.key] = replace(spec, module=found.name)
    return specs


#: Blocks declared by types that are not yet modules of their own, filled in
#: as their tables register (:func:`.breadth.register`).
DECLARED_BLOCKS: dict[str, int] = {}


@cache
def _discovered_blocks() -> dict[str, int]:
    return {
        key: spec.part_number_block
        for key, spec in discover().items()
        if spec.part_number_block is not None
    }


def part_number_block(type_key: str) -> int:
    """The block a type's key derives: a hash, so no list hands blocks out."""
    digest = int(hashlib.sha256(type_key.encode("utf-8")).hexdigest(), 16)
    return digest % (BLOCK_HIGH - BLOCK_LOW + 1) + BLOCK_LOW


def block_of(type_key: str) -> int:
    """The block a type's identifiers carry: its own declared one, else the derived one."""
    declared = _discovered_blocks().get(type_key, DECLARED_BLOCKS.get(type_key))
    return part_number_block(type_key) if declared is None else declared


def check_collisions(blocks: Mapping[str, int]) -> None:
    """Refuse two types on one block, naming both, in key order."""
    owner: dict[int, str] = {}
    clashes: list[str] = []
    for key in sorted(blocks):
        block = blocks[key]
        if not BLOCK_LOW <= block <= BLOCK_HIGH:
            raise TypeCollisionError(f"{key}'s part-number block {block} is not four digits")
        if block in owner:
            clashes.append(f"{owner[block]} and {key} both use block {block:04d}")
        else:
            owner[block] = key
    if clashes:
        raise TypeCollisionError(
            "part-number blocks collide: "
            + "; ".join(clashes)
            + ". Give one of each pair its own part_number_block= in its type module."
        )


def part_number(block: int, sequence: int) -> str:
    """``4127046271``: the type's block, then its scrambled per-type sequence."""
    if not 0 <= sequence < SEQUENCE_SPACE:
        raise ValueError(f"block {block:04d} has used all {SEQUENCE_SPACE} part numbers")
    return f"{block:04d}{(sequence * _PART_STRIDE) % SEQUENCE_SPACE:06d}"


def type_rng(seed: int, type_key: str) -> random.Random:
    """The type's own random stream, from the seed and its key alone."""
    return random.Random(f"{seed}:{type_key}")
