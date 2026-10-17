"""Serum (gen#214): active and skin concern are attributes, the size in ml is the SKU.

See :mod:`beauty_depth` for the nine types, the colors and the decoy classes; :mod:`kit_beauty`
draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from functools import partial

from beauty_depth import PACK_INK, PACK_SAGE, PACK_SAND, PACK_SKY, decoy, row
from type_registry import Decoy, TypeSpec, a

_row = partial(row, path=("Beauty", "Skincare", "Serums"), ptype="Serum")

ROWS = (
    _row("SRMRET", "Retinol Night Serum", "Thornlea Skin", 24.0, "serum",
        "A night serum with encapsulated retinol that smooths the look of lines.",
        (a("active", "Active", "Retinol"), a("skin_concern", "Skin concern", "Fine Lines")), (("15", 24.0), ("30", 38.0)), "net_volume_ml", (("form", "dropper"),), (PACK_INK,)),
    _row("SRMVTC", "Vitamin C Brightening Serum", "Fenmere", 20.0, "serum",
        "A fresh daily serum with stabilised vitamin C to wake up skin that looks tired.",
        (a("active", "Active", "Vitamin C"), a("skin_concern", "Skin concern", "Dullness")), (("15", 20.0), ("30", 32.0), ("50", 44.0)), "net_volume_ml", (("form", "dropper"),), (PACK_SAND,)),
    _row("SRMHYA", "Hyaluronic Acid Hydrating Serum", "Pearlbrook", 18.0, "serum",
        "A water-light serum with three weights of hyaluronic acid that plumps and comforts.",
        (a("active", "Active", "Hyaluronic Acid"), a("skin_concern", "Skin concern", "Dryness")), (("30", 18.0), ("50", 26.0)), "net_volume_ml", (("form", "pump"),), (PACK_SKY,)),
    _row("SRMNIA", "Niacinamide Pore Serum", "Thornlea Skin", 15.0, "serum",
        "A lightweight serum with ten percent niacinamide that tightens the look of enlarged pores.",
        (a("active", "Active", "Niacinamide"), a("skin_concern", "Skin concern", "Blemishes")), (("30", 15.0), ("50", 22.0)), "net_volume_ml", (("form", "pump"),), (PACK_SAGE,)),
)  # fmt: skip

SPEC = TypeSpec(
    key="serum",
    department="Beauty",
    product_type="Serum",
    rows=ROWS,
    decoys=(
        Decoy(4, "vitamin c serum", "vocabulary", decoy("SRD1", "Vitamin C Orange Cap Serum", "A retinol serum with an orange cap.", ROWS[0])),
        Decoy(6, "vitamin c serum", "generic", decoy("SRD2", "Vitamin C Grove Night Serum", "From the Vitamin C Grove range: a retinol night serum.", ROWS[0])),
        Decoy(7, "vitamin c serum", "generic", decoy("SRD3", "Night Serum", "A retinol night serum.", ROWS[0], brand="Vitamin C Orchard")),
    ),
    owners=(("Fenmere", "third_party"), ("Pearlbrook", "third_party"), ("Thornlea Skin", "third_party"), ("Vitamin C Orchard", "third_party"),),
)  # fmt: skip
