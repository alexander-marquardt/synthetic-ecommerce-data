"""Incontinence pads (gen#968, slice 3): Health > Incontinence > Incontinence Pads.

A breadth type (``derivable``): the scaled build draws more packs by swapping the absorbency the
title shows. A SKU is a pack of 10 to 48 pads (``piece_count``). The drawing is a soft pack with
a pad on its front and one drop per absorbency step, a moon for overnight
(:func:`kit_health_care.pad_pack`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_health_care,  # noqa: F401 -- registers pad_pack
)
from synthetic_ecommerce_data.domains.retail.health_rows import (
    BLUE,
    GREEN,
    GREY,
    HALVERING,
    OWNERS,
    QUELLMOOR,
    ROOT,
    THRENNICK,
    VELLING,
    counts,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_PATH = (ROOT, "Incontinence", "Incontinence Pads")


def _pads(code, title, brand, absorbency, sizes, desc, color=BLUE) -> object:  # noqa: ANN001
    return row(code, title, brand, _PATH, "Incontinence Pads", "pad_pack", desc,
               (a("pad_absorbency", "Absorbency", absorbency),), ("absorbency", absorbency.lower()),
               sizes, color=color)  # fmt: skip


ROWS = (
    _pads("HIPLGT", "Light Incontinence Pads", VELLING, "Light", counts((12, 3.0), (24, 5.5), (48, 10.0)),
          "Slim, discreet pads for light bladder leaks, each one wrapped on its own."),
    _pads("HIPMED", "Medium Incontinence Pads", QUELLMOOR, "Medium", counts((12, 3.5), (24, 6.5)),
          "Contoured pads with a soft cover and a breathable back, each one wrapped on its own.", GREEN),
    _pads("HIPHVY", "Heavy Incontinence Pads", HALVERING, "Heavy", counts((10, 4.0), (20, 7.5)),
          "Longer, thicker pads with raised side edges for heavier leaks."),
    _pads("HIPNGT", "Overnight Incontinence Pads", THRENNICK, "Overnight", counts((10, 4.5), (20, 8.5)),
          "The longest pads in the range, with a wider back for a full night's sleep.", GREY),
    _pads("HIPMEN", "Light Incontinence Pads for Men", HALVERING, "Light", counts((14, 4.0), (28, 7.5)),
          "Cup-shaped pads that sit in close-fitting underwear, each one wrapped on its own.", GREY),
)  # fmt: skip

#: Text-match decoys: the title names a range holding the query's word, the fields say a lighter
#: absorbency, so only a policy that reads ``pad_absorbency`` puts the real packs first.
DECOYS = (
    Decoy(6, "overnight incontinence pads", "generic", decoy(
        ROWS[0], "HIPDY1", "Overnight Bag Light Incontinence Pads",
        "From the Overnight Bag travel range: slim light pads, each one wrapped on its own.")),
    Decoy(6, "heavy incontinence pads", "generic", decoy(
        ROWS[1], "HIPDY2", "Heavy Rain Medium Incontinence Pads",
        "From the Heavy Rain range: contoured medium pads with a soft cover.")),
)  # fmt: skip

SPEC = TypeSpec(
    key="incontinence_pads",
    department="Health",
    product_type="Incontinence Pads",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=DECOYS,
)
