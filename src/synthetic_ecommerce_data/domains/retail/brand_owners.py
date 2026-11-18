"""Who owns each breadth brand, resolved the same way in any interpreter (gen#1039).

Nothing writes an owner at import time. :data:`breadth_row.OWNERS` is the read-only base table,
each module in :data:`SOURCES` states its brands as a constant ``OWNED`` (pairs of brand and
``"own"`` or ``"third_party"``), and every spec of ``type_specs`` states its own in
``TypeSpec.owners``. :func:`table` imports them all and merges them, so the answer does not
depend on what was imported first. A brand two sources give different owners raises
:class:`OwnerConflict` naming both: a first-wins merge once hid ``beach_towel`` calling two of the
shop's own brands third party. ``tests/test_brand_owners_1039.py`` fails when a module states
``OWNED`` and is not in :data:`SOURCES`, or when any module writes ``OWNERS``.
"""

from __future__ import annotations

import functools
import importlib
import pkgutil
from collections.abc import Iterable, Mapping
from types import MappingProxyType

_PACKAGE = __name__.rpartition(".")[0]

#: Every retail module that states brands in a module-level ``OWNED``, in the order :func:`table`
#: merges them. The specs of ``type_specs`` are found by walking the package.
SOURCES = (
    "accessory_rows",
    "barry_plotter",
    "color_word_brand_rows",
    "decoy_rows",
    "decoy_word_kinds",
    "gadgets_rows",
    "hair_rows",
    "jewellery_rows",
    "kids_depth_rows",
    "kids_films",
    "knacks_rows",
    "knitwear_rows",
    "lowerbody_rows",
    "luggage_common",
    "mens_depth_rows",
    "misspelled_brands",
    "neckline_rows",
    "school_rows",
    "swimwear_rows",
    "womens_depth_rows",
)


class OwnerConflict(ValueError):
    """Two sources give one brand different owners."""


def merge(sources: Iterable[tuple[str, Iterable[tuple[str, str]]]]) -> dict[str, str]:
    """One owner per brand from ``(source name, (brand, owner) pairs)``: :class:`OwnerConflict`
    when two sources disagree on a brand, naming the brand, both owners and both sources."""
    owners: dict[str, str] = {}
    said_by: dict[str, str] = {}
    for name, pairs in sources:
        for brand, owner in pairs:
            if owners.setdefault(brand, owner) != owner:
                raise OwnerConflict(
                    f"{brand!r} is {owners[brand]!r} in {said_by[brand]} and {owner!r} in {name}"
                )
            said_by.setdefault(brand, name)
    return owners


def _sources() -> list[tuple[str, Iterable[tuple[str, str]]]]:
    from synthetic_ecommerce_data.domains.retail import type_specs
    from synthetic_ecommerce_data.domains.retail.breadth_row import OWNERS

    found: list[tuple[str, Iterable[tuple[str, str]]]] = [("breadth_row", OWNERS.items())]
    for name in SOURCES:
        found.append((name, importlib.import_module(f"{_PACKAGE}.{name}").OWNED))
    for info in pkgutil.iter_modules(type_specs.__path__):
        spec = getattr(importlib.import_module(f"{type_specs.__name__}.{info.name}"), "SPEC", None)
        found.append((f"type_specs/{info.name}", getattr(spec, "owners", ())))
    return found


@functools.cache
def table() -> Mapping[str, str]:
    """Every breadth brand's owner (``"own"`` or ``"third_party"``), the same in any interpreter."""
    return MappingProxyType(merge(_sources()))


def owner(brand: str) -> str:
    """``brand``'s owner from :func:`table`: ``KeyError`` for a brand no source states."""
    return table()[brand]
