"""Body Mist (gen#214): the fragrance family is an attribute, fragrance x size in ml are the SKUs.

See :mod:`beauty_depth` for the nine types, the colors and the decoy classes; :mod:`kit_beauty`
draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from functools import partial

from beauty_depth import PACK_ROSE, PACK_SAND, PACK_SKY, decoy, row
from type_registry import Decoy, TypeSpec, a

_row = partial(row, path=("Beauty", "Fragrance", "Body Mists"), ptype="Body Mist")

ROWS = (
    _row("BMSFLR", "Peony Blossom Body Mist", "Fenmere", 7.0, "body_mist",
        "A light, floral veil of petals to spritz over skin and clothes.",
        (a("fragrance_family", "Fragrance family", "Floral"),),
        (("100", 7.0), ("250", 12.0)), "net_volume_ml", (("cap", "dome"),), (PACK_ROSE,), option=("fragrance", ("Peony", "Rose", "Jasmine"))),
    _row("BMSFRT", "Berry Burst Body Mist", "Sorrel & Salt", 6.0, "body_mist",
        "A juicy, sparkling mist of summer berries.",
        (a("fragrance_family", "Fragrance family", "Fruity"),),
        (("100", 6.0), ("250", 11.0)), "net_volume_ml", (("cap", "ring"),), (PACK_SKY,), option=("fragrance", ("Strawberry", "Peach", "Cherry"))),
    _row("BMSGRM", "Vanilla Sugar Body Mist", "Veilmoor", 7.5, "body_mist",
        "A warm, sweet mist that smells like fresh baking.",
        (a("fragrance_family", "Fragrance family", "Gourmand"),),
        (("100", 7.5), ("250", 13.0)), "net_volume_ml", (("cap", "dome"),), (PACK_SAND,), option=("fragrance", ("Vanilla", "Caramel", "Coconut"))),
)  # fmt: skip

SPEC = TypeSpec(
    key="body_mist",
    department="Beauty",
    product_type="Body Mist",
    rows=ROWS,
    decoys=(
        Decoy(4, "vanilla body mist", "vocabulary", decoy("BMD1", "Vanilla Cap Floral Body Mist", "A floral mist in a bottle with a vanilla-colored cap.", ROWS[0])),
        Decoy(6, "vanilla body mist", "generic", decoy("BMD2", "Vanilla Bay Floral Body Mist", "From the Vanilla Bay range: a floral mist.", ROWS[0])),
        Decoy(7, "vanilla body mist", "generic", decoy("BMD3", "Floral Body Mist", "A light floral mist.", ROWS[0], brand="Vanilla Wren")),
    ),
    owners=(("Fenmere", "third_party"), ("Sorrel & Salt", "third_party"), ("Vanilla Wren", "third_party"), ("Veilmoor", "third_party"),),
)  # fmt: skip
