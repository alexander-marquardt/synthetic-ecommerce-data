"""Fridges and freezers (gen#334): eight kinds of six models in Home > Large Appliances.

70/30 and 50/50 fridge freezers, an American style side-by-side, an under-counter fridge, a
larder fridge, a chest freezer, an upright freezer and an integrated fridge, drawn by
:func:`kit_large_appliances.fridge`. A model's capacity, width, energy rating and frost-free
entry are structured; its finish is the SKU's color. The retro 50/50 models come in the six
main colors (gen#275). The two color decoys name a color in the title that the product is not:
a "Black Edition" fridge that is stainless steel, a "Red Line" larder fridge that is white.
Every brand name is invented. Not derivable: the range is authored.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

import large_appliance_rows as rows
from type_registry import Decoy, Row, TypeSpec, a

_PTYPE = "Fridge & Freezer"

SPEC = TypeSpec(
    key="fridge_freezer",
    department="Home",
    product_type=_PTYPE,
    owners=rows.OWNERS,
    rows=rows.fridge_rows(),
    decoys=(
        Decoy(4, "black fridge", "color", Row(
            "FDB001", "Black Edition Fridge Freezer", rows.BRANDS[0], "Home", rows.FRIDGES, _PTYPE,
            449.0, "fridge", "The Black Edition range in brushed stainless steel, a 70/30 fridge "
            "freezer with frost free cooling.", (rows.SILVER,),
            (a("appliance_type", "Type", "Fridge Freezer 70/30"), a("finish", "Finish", "Stainless Steel")),
            params=(("kind", "fridge_freezer_7030"),))),
        Decoy(1, "red fridge", "color", Row(
            "FDB002", "Red Line Larder Fridge", rows.BRANDS[1], "Home", rows.FRIDGES, _PTYPE, 329.0,
            "fridge", "A larder fridge from the Red Line range, finished in white, with glass shelves.",
            (rows.WHITE,), (a("appliance_type", "Type", "Larder Fridge"),),
            params=(("kind", "larder"),))),
    ),
)
