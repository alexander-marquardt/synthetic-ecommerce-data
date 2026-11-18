"""Who owns each breadth brand, resolved the same way in any interpreter (gen#1039).

:data:`breadth_row.OWNERS` starts with the base brands, and the modules in :data:`SOURCES` add
theirs when they are imported, as does every spec of ``type_specs`` (``TypeSpec.owners``). Read
directly, that dict holds only what this interpreter happened to import first, so a row's
``doc()`` raised ``KeyError`` for a brand whose module had not been imported (``electronics_rows``
alone: ``KeyError: 'Halvern'``). :func:`table` imports every source and every spec before it
answers, so the answer does not depend on import order. ``tests/test_brand_owners_1039.py``
fails when a module writes ``OWNERS`` and is not in :data:`SOURCES`.
"""

from __future__ import annotations

import functools
import importlib
import pkgutil
from collections.abc import Mapping
from types import MappingProxyType

_PACKAGE = __name__.rpartition(".")[0]

#: Every retail module that adds brands to :data:`breadth_row.OWNERS` when it is imported, in the
#: order :func:`table` imports them. The specs of ``type_specs`` are found by walking the package.
SOURCES = (
    "accessory_rows",
    "barry_plotter",
    "color_word_brand_rows",
    "decoy_rows",
    "decoy_word_kinds",
    "gadgets_rows",
    "hair_rows",
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
    "womens_depth_rows",
)


@functools.cache
def table() -> Mapping[str, str]:
    """Every breadth brand's owner (``"own"`` or ``"third_party"``), the same in any interpreter."""
    from synthetic_ecommerce_data.domains.retail import type_specs
    from synthetic_ecommerce_data.domains.retail.breadth_row import OWNERS

    for name in SOURCES:
        importlib.import_module(f"{_PACKAGE}.{name}")
    # A spec registers its ``owners`` when it is built, so importing the module is enough.
    for info in pkgutil.iter_modules(type_specs.__path__):
        importlib.import_module(f"{type_specs.__name__}.{info.name}")
    return MappingProxyType(dict(OWNERS))


def owner(brand: str) -> str:
    """``brand``'s owner from :func:`table`: ``KeyError`` for a brand no source states."""
    return table()[brand]
