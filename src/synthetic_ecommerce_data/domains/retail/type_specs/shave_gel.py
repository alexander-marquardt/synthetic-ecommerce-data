"""Shave gel (gen#1112, slice 3): Beauty > Shaving > Shave Gel.

A breadth type (``derivable``): the title shows the scent and the skin type the gel is made for
(sensitive, normal, dry), and the scaled build draws more cans by swapping them. A SKU is a can
of 150 to 300 ml (``net_volume_ml``). The drawing is a can under its actuator with a band in the
scent's tone (:func:`kit_bath_shave.shave_gel_can`). gen#957's Aftershave is the step after it.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.bath_shave_rows import (
    FENMERE,
    NAVY,
    OWNERS,
    SHAVING,
    SLATE,
    SORREL,
    TEAL,
    THORNLEA,
    VEILMOOR,
    decoy,
    row,
    sizes,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_PT = "Shave Gel"


def _can(code, title, brand, scent, skin, skus, desc, color=NAVY) -> object:  # noqa: ANN001
    attrs = (a("scent", "Scent", scent), a("skin_type", "Skin type", skin))
    return row(code, title, brand, (*SHAVING, _PT), _PT, "shave_gel_can", desc, attrs, skus,
               "net_volume_ml", color, "Shave Gel")  # fmt: skip


ROWS = (
    _can("SHGALS", "Aloe Vera Shave Gel for Sensitive Skin", THORNLEA, "Aloe Vera", "Sensitive",
         sizes((150, 3.0), (200, 3.75), (300, 5.0)), "A clear gel that turns to a thick lather in wet hands, so the blade glides."),
    _can("SHGMEN", "Menthol Shave Gel for Normal Skin", VEILMOOR, "Menthol", "Normal",
         sizes((150, 2.5), (200, 3.25), (300, 4.5)), "A gel that lathers up in seconds and rinses off the blade without clogging it.", TEAL),
    _can("SHGSAD", "Sandalwood Shave Gel for Dry Skin", FENMERE, "Sandalwood", "Dry",
         sizes((150, 4.0), (200, 5.0), (300, 6.5)), "A rich gel worked into stubble with the fingertips, for a close shave.", SLATE),
    _can("SHGUNN", "Unscented Shave Gel for Normal Skin", SORREL, "Unscented", "Normal",
         sizes((150, 2.75), (200, 3.5), (300, 4.75)), "A gel in a can with a clear stripe, so the shaver sees how much is left."),
    _can("SHGCOS", "Coconut Shave Gel for Sensitive Skin", THORNLEA, "Coconut", "Sensitive",
         sizes((150, 3.25), (200, 4.0), (300, 5.25)), "A gel that spreads thin on the legs and the face alike and rinses off clean.", TEAL),
)  # fmt: skip

#: Text-match decoys: the title names a range holding the query's word, the fields say another
#: scent or skin type, so only a policy that reads ``scent`` or ``skin_type`` puts the real cans
#: first.
DECOYS = (
    Decoy(6, "menthol shave gel", "generic", decoy(
        ROWS[2], "SHGDY1", "Menthol Ridge Sandalwood Shave Gel for Dry Skin",
        "From the Menthol Ridge range: a rich gel worked into stubble with the fingertips.")),
    Decoy(6, "sensitive shave gel", "generic", decoy(
        ROWS[1], "SHGDY2", "Sensitive Point Menthol Shave Gel for Normal Skin",
        "From the Sensitive Point range: a gel that lathers up in seconds.")),
)  # fmt: skip

SPEC = TypeSpec(
    key="shave_gel",
    department="Beauty",
    product_type=_PT,
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=DECOYS,
)
