"""Aftershave (gen#214): fragrance family and concentration are attributes, the size in ml is the SKU.

See :mod:`beauty_depth` for the nine types, the colors and the decoy classes; :mod:`kit_beauty`
draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from functools import partial

from beauty_depth import PACK_INK, PACK_SAND, PACK_SKY, decoy, row
from type_registry import Decoy, TypeSpec, a

_row = partial(row, path=("Beauty", "Fragrance", "Aftershave"), ptype="Aftershave")

ROWS = (
    _row("ASHWDY", "Cedar Woods Aftershave", "Thornlea Skin", 14.0, "aftershave",
        "A calming splash of cedar and oak moss for freshly shaved skin.",
        (a("fragrance_family", "Fragrance family", "Woody"), a("concentration", "Concentration", "Aftershave Splash")), (("50", 14.0), ("100", 22.0)), "net_volume_ml", (("cap", "stopper"),), (PACK_INK,)),
    _row("ASHFRS", "Ocean Fresh Eau de Toilette for Men", "Aldermist", 24.0, "aftershave",
        "A clean, salty eau de toilette with sea notes and a crisp finish.",
        (a("fragrance_family", "Fragrance family", "Aquatic"), a("concentration", "Concentration", "Eau de Toilette")), (("50", 24.0), ("100", 36.0)), "net_volume_ml", (("cap", "spray"),), (PACK_SKY,)),
    _row("ASHSPC", "Black Pepper Eau de Cologne", "Pearlbrook", 18.0, "aftershave",
        "A warm, spicy cologne with pepper and amber for evenings out.",
        (a("fragrance_family", "Fragrance family", "Spicy"), a("concentration", "Concentration", "Eau de Cologne")), (("50", 18.0), ("100", 28.0)), "net_volume_ml", (("cap", "stopper"),), (PACK_SAND,)),
)  # fmt: skip

SPEC = TypeSpec(
    key="aftershave",
    department="Beauty",
    product_type="Aftershave",
    rows=ROWS,
    decoys=(
        Decoy(4, "citrus aftershave", "vocabulary", decoy("ASD1", "Citrus Stopper Woody Aftershave", "A woody aftershave with a citrus-green stopper.", ROWS[0])),
        Decoy(6, "citrus aftershave", "generic", decoy("ASD2", "Citrus Bay Woody Aftershave", "From the Citrus Bay range: a woody aftershave.", ROWS[0])),
        Decoy(7, "citrus aftershave", "generic", decoy("ASD3", "Woody Aftershave", "A woody aftershave splash.", ROWS[0], brand="Citrus Heron")),
    ),
    owners=(("Aldermist", "third_party"), ("Citrus Heron", "third_party"), ("Pearlbrook", "third_party"), ("Thornlea Skin", "third_party"),),
)  # fmt: skip
