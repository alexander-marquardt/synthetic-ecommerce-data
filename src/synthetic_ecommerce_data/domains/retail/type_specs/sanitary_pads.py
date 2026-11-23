"""Sanitary pads (gen#1112, slice 1): Health > Feminine Care > Sanitary Pads.

A breadth type (``derivable``): the title shows the pad's thickness, its absorbency and its
wings, and the scaled build draws more packs by swapping them. A SKU is a pack of 10 to 42 pads
(``piece_count``). The drawing is a soft pack with a pad on its front, its wings out or not, a thin
or a thick edge, one drop per absorbency step and a moon for overnight
(:func:`kit_health_feminine.sanitary_pad_pack`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.feminine_care_rows import PURPLE, TEAL, row
from synthetic_ecommerce_data.domains.retail.health_rows import (
    HALVERING,
    OWNERS,
    QUELLMOOR,
    THRENNICK,
    VELLING,
    counts,
    decoy,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _pads(code, title, brand, thickness, absorbency, wings, sizes, desc, color=None) -> object:  # noqa: ANN001
    attrs = (a("pad_thickness", "Pad thickness", thickness), a("pad_absorbency", "Absorbency", absorbency),
             a("pad_wings", "Wings", wings))
    extra = {"color": color} if color else {}
    return row(code, title, brand, "Sanitary Pads", "sanitary_pad_pack", desc, attrs, sizes, **extra)


ROWS = (
    _pads("HFSUTR", "Ultra Thin Regular Sanitary Pads With Wings", VELLING, "Ultra Thin", "Regular", "With Wings",
          counts((14, 2.25), (28, 4.0), (42, 5.5)), "Soft-cover pads, each one wrapped on its own, in a resealable pack."),
    _pads("HFSUTL", "Ultra Thin Long Sanitary Pads With Wings", QUELLMOOR, "Ultra Thin", "Long", "With Wings",
          counts((12, 2.5), (24, 4.5)), "Pads with a breathable back and a cotton-feel cover, folded into their own wrapper."),
    _pads("HFSMXS", "Maxi Super Sanitary Pads Without Wings", HALVERING, "Maxi", "Super", "Without Wings",
          counts((12, 2.0), (24, 3.75), (36, 5.25)), "Cushioned pads with a quilted top sheet and a stay-put adhesive strip."),
    _pads("HFSMXN", "Maxi Overnight Sanitary Pads With Wings", THRENNICK, "Maxi", "Overnight", "With Wings",
          counts((10, 2.5), (20, 4.5)), "The fullest pads in the range, with a wider back for a full night's sleep.", PURPLE),
    _pads("HFSUTX", "Ultra Thin Light Sanitary Pads Without Wings", VELLING, "Ultra Thin", "Light", "Without Wings",
          counts((16, 2.0), (32, 3.5)), "Slim, discreet pads that tuck into a pocket in a soft pouch."),
    _pads("HFSMXR", "Maxi Regular Sanitary Pads With Wings", QUELLMOOR, "Maxi", "Regular", "With Wings",
          counts((14, 2.0), (28, 3.75), (42, 5.25)), "Plump pads with a fluffy core, sold in a value bag of individually sealed pads.", TEAL),
)  # fmt: skip

#: Text-match decoys: the title names a range holding the query's word, the fields say another
#: absorbency or thickness, so only a policy that reads ``pad_absorbency`` or ``pad_thickness``
#: puts the real packs first.
DECOYS = (
    Decoy(6, "overnight sanitary pads", "generic", decoy(
        ROWS[0], "HFSDY1", "Overnight Glow Ultra Thin Regular Sanitary Pads With Wings",
        "From the Overnight Glow range: soft-cover pads, each one wrapped on its own.")),
    Decoy(6, "maxi sanitary pads", "generic", decoy(
        ROWS[4], "HFSDY2", "Maxi Bloom Ultra Thin Light Sanitary Pads Without Wings",
        "From the Maxi Bloom range: slim, discreet pads in a soft pouch.")),
)  # fmt: skip

SPEC = TypeSpec(
    key="sanitary_pads",
    department="Health",
    product_type="Sanitary Pads",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=DECOYS,
)
