"""Who owns each breadth brand, resolved the same way in any interpreter (gen#1039).

No module writes an owner when it is imported. :data:`breadth_row.OWNERS` is the read-only base
table. Each module in :data:`SOURCES` states its brands in a module-level ``OWNED`` constant
(pairs of brand and ``"own"`` or ``"third_party"``), and every spec of ``type_specs`` states its
own in ``TypeSpec.owners``. :func:`table` reads all of them and merges them, so its answer does
not depend on what this interpreter imported first. Read straight from ``OWNERS``, a row's
``doc()`` used to raise ``KeyError`` for a brand whose module had not been imported yet
(``electronics_rows`` alone: ``KeyError: 'Halvern'``).

Two sources that give one brand different owners raise :class:`OwnerConflict`, which names the
brand and both sources. The old import-time writes kept whichever owner came first, so
``beach_towel``'s ``third_party`` for ``Harbour & Pine`` was dropped without a word.
``tests/test_brand_owners_1039.py`` fails when a module states ``OWNED`` and is not in
:data:`SOURCES`, or writes ``OWNERS``.
"""

from __future__ import annotations

import functools
import importlib
import pkgutil
from collections.abc import Iterable, Mapping
from types import MappingProxyType

_PACKAGE = __name__.rpartition(".")[0]

#: Every retail module that states brand owners in a module-level ``OWNED``, in the order
#: :func:`table` reads them. The specs of ``type_specs`` are found by walking the package.
SOURCES = (
    "accessory_rows",
    "barry_plotter",
    "color_word_brand_rows",
    "decoy_rows",
    "decoy_word_kinds",
    "fishing_golf_rows",
    "gadgets_rows",
    "grooming_rows",
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
    "skin_rows",
    "swimwear_rows",
    "womens_depth_rows",
)


class OwnerConflict(ValueError):
    """Two sources give one brand different owners."""


def merge(sources: Iterable[tuple[str, Iterable[tuple[str, str]]]]) -> dict[str, str]:
    """One owner per brand from ``(source name, (brand, owner) pairs)``.

    A brand that two sources state with the same owner is fine. A brand they state with different
    owners raises :class:`OwnerConflict`: no source wins by coming first.
    """
    seen: dict[str, tuple[str, str]] = {}
    for source, pairs in sources:
        for brand, owner_ in pairs:
            first = seen.setdefault(brand, (owner_, source))
            if first[0] != owner_:
                raise OwnerConflict(
                    f"{brand!r} is {first[0]!r} in {first[1]} and {owner_!r} in {source}: "
                    "a brand has one owner"
                )
    return {brand: owner_ for brand, (owner_, _) in seen.items()}


def sources() -> list[tuple[str, tuple[tuple[str, str], ...]]]:
    """Every source of owners by name: the base table, each ``OWNED`` and each spec's ``owners``."""
    from synthetic_ecommerce_data.domains.retail import type_specs
    from synthetic_ecommerce_data.domains.retail.breadth_row import OWNERS

    found = [("breadth_row.OWNERS", tuple(OWNERS.items()))]
    for name in SOURCES:
        found.append((f"{name}.OWNED", tuple(importlib.import_module(f"{_PACKAGE}.{name}").OWNED)))
    for info in pkgutil.iter_modules(type_specs.__path__):
        spec = getattr(importlib.import_module(f"{type_specs.__name__}.{info.name}"), "SPEC", None)
        found.append((f"type_specs/{info.name}.py", tuple(getattr(spec, "owners", ()))))
    return found


@functools.cache
def table() -> Mapping[str, str]:
    """Every breadth brand's owner (``"own"`` or ``"third_party"``), the same in any interpreter."""
    return MappingProxyType(merge(sources()))


def owner(brand: str) -> str:
    """``brand``'s owner from :func:`table`: ``KeyError`` for a brand no source states."""
    return table()[brand]
