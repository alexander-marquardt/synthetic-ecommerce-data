"""Face Mask (gen#214): mask type and skin concern are attributes, the pack count is the SKU.

See :mod:`beauty_depth` for the nine types, the colors and the decoy classes; :mod:`kit_beauty`
draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from functools import partial

from beauty_depth import PACK_ROSE, PACK_SAGE, PACK_SKY, decoy, row
from type_registry import Decoy, TypeSpec, a

_row = partial(row, path=("Beauty", "Skincare", "Face Masks"), ptype="Face Mask")

ROWS = (
    _row("FMSSHT", "Hydrating Sheet Face Mask", "Pearlbrook", 2.5, "face_mask",
        "A soaked cotton sheet mask that leaves skin soft and bouncy in fifteen minutes.",
        (a("mask_type", "Mask type", "Sheet"), a("skin_concern", "Skin concern", "Dryness")), (("1", 2.5), ("5", 11.0), ("10", 20.0)), "units_per_pack", (("mask", "sheet"),), (PACK_SKY,)),
    _row("FMSCLY", "Purifying Clay Face Mask", "Thornlea Skin", 9.0, "face_mask",
        "A rinse-off kaolin mask that draws out oil and clears the look of pores.",
        (a("mask_type", "Mask type", "Clay"), a("skin_concern", "Skin concern", "Blemishes")), (("1", 9.0), ("2", 16.0), ("3", 22.0)), "units_per_pack", (("mask", "clay"),), (PACK_SAGE,)),
    _row("FMSNGT", "Overnight Repair Face Mask", "Aldermist", 14.0, "face_mask",
        "A rich leave-on mask that works while you sleep to smooth the look of lines.",
        (a("mask_type", "Mask type", "Overnight"), a("skin_concern", "Skin concern", "Fine Lines")), (("1", 14.0), ("2", 26.0)), "units_per_pack", (("mask", "overnight"),), (PACK_ROSE,)),
)  # fmt: skip

SPEC = TypeSpec(
    key="face_mask",
    department="Beauty",
    product_type="Face Mask",
    rows=ROWS,
    decoys=(
        Decoy(4, "clay face mask", "vocabulary", decoy("FMD1", "Clay Pot Sheet Face Mask", "A sheet mask that comes with a clay pot-style sachet.", ROWS[0])),
        Decoy(6, "clay face mask", "generic", decoy("FMD2", "Clay Hill Sheet Face Mask", "From the Clay Hill range: a sheet mask.", ROWS[0])),
        Decoy(7, "clay face mask", "generic", decoy("FMD3", "Sheet Face Mask", "A hydrating sheet mask.", ROWS[0], brand="Clay Wren")),
    ),
    owners=(("Aldermist", "third_party"), ("Clay Wren", "third_party"), ("Pearlbrook", "third_party"), ("Thornlea Skin", "third_party"),),
)  # fmt: skip
