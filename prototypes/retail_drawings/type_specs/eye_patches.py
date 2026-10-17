"""Eye Patches (gen#214): patch type and skin concern are attributes, the pack count (pairs) is the SKU.

See :mod:`beauty_depth` for the nine types, the colors and the decoy classes; :mod:`kit_beauty`
draws them.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from functools import partial

from beauty_depth import PACK_ROSE, PACK_SAND, PACK_SKY, decoy, row
from type_registry import Decoy, TypeSpec, a

_row = partial(row, path=("Beauty", "Skincare", "Eye Patches"), ptype="Eye Patches")

ROWS = (
    _row("EYPHYD", "Hydrogel Eye Patches", "Aldermist", 8.0, "eye_patches",
        "Cooling hydrogel patches that ease a puffy morning look in ten minutes.",
        (a("patch_type", "Patch type", "Hydrogel"), a("skin_concern", "Skin concern", "Puffiness")), (("6", 8.0), ("30", 24.0)), "units_per_pack", (("patch", "hydrogel"),), (PACK_SKY,)),
    _row("EYPCOL", "Collagen Under Eye Patches", "Sorrel & Salt", 10.0, "eye_patches",
        "Soft cloth patches with marine collagen to smooth the fine skin under the eye.",
        (a("patch_type", "Patch type", "Cloth"), a("skin_concern", "Skin concern", "Fine Lines")), (("8", 10.0), ("24", 26.0)), "units_per_pack", (("patch", "cloth"),), (PACK_ROSE,)),
    _row("EYPGLD", "Brightening Gel Eye Patches", "Veilmoor", 12.0, "eye_patches",
        "Gel patches with caffeine that brighten the look of tired eyes.",
        (a("patch_type", "Patch type", "Gel"), a("skin_concern", "Skin concern", "Dark Circles")), (("6", 12.0), ("30", 34.0)), "units_per_pack", (("patch", "hydrogel"),), (PACK_SAND,)),
)  # fmt: skip

SPEC = TypeSpec(
    key="eye_patches",
    department="Beauty",
    product_type="Eye Patches",
    rows=ROWS,
    decoys=(
        Decoy(4, "cloth eye patches", "vocabulary", decoy("EPD1", "Cloth Pouch Eye Patches", "Hydrogel patches in a cloth pouch.", ROWS[0])),
        Decoy(6, "cloth eye patches", "generic", decoy("EPD2", "Cloth Hill Eye Patches", "From the Cloth Hill range: hydrogel patches.", ROWS[0])),
        Decoy(7, "cloth eye patches", "generic", decoy("EPD3", "Hydrogel Eye Patches", "Cooling hydrogel patches.", ROWS[0], brand="Cloth Wren")),
    ),
    owners=(("Aldermist", "third_party"), ("Cloth Wren", "third_party"), ("Sorrel & Salt", "third_party"), ("Veilmoor", "third_party"),),
)  # fmt: skip
