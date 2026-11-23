"""Panty liners (gen#1112, slice 1): Health > Feminine Care > Panty Liners.

A breadth type (``derivable``): the title shows the liner's length and its scent, and the scaled
build draws more packs by swapping them. A SKU is a pack of 16 to 60 liners (``piece_count``). The
drawing is a flat box with one liner in front, drawn to its length, a sprig for a fresh scent and a leaf for aloe
(:func:`kit_health_feminine.liner_pack`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.feminine_care_rows import LILAC, PURPLE, TEAL, row
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


def _liners(code, title, brand, length, scent, sizes, desc, color=None) -> object:  # noqa: ANN001
    attrs = (a("liner_length", "Liner length", length), a("scent", "Scent", scent))
    extra = {"color": color} if color else {}
    return row(code, title, brand, "Panty Liners", "liner_pack", desc, attrs, sizes, **extra)


ROWS = (
    _liners("HFLRUN", "Regular Unscented Panty Liners", VELLING, "Regular", "Unscented",
            counts((20, 1.25), (40, 2.25), (60, 3.0)), "Thin, flexible liners for every day, each one folded in its own wrapper."),
    _liners("HFLLUN", "Long Unscented Panty Liners", QUELLMOOR, "Long", "Unscented",
            counts((20, 1.5), (40, 2.75)), "Liners with a breathable back and a soft cotton-feel top."),
    _liners("HFLXFS", "Extra Long Fresh Scent Panty Liners", HALVERING, "Extra Long", "Fresh Scent",
            counts((18, 1.6), (36, 2.9)), "Wide liners that reach further back, with a stay-put adhesive strip."),
    _liners("HFLRFS", "Regular Fresh Scent Panty Liners", THRENNICK, "Regular", "Fresh Scent",
            counts((24, 1.4), (48, 2.6)), "Compact liners that fold small for a handbag, in a slim box.", LILAC),
    _liners("HFLLAL", "Long Aloe Panty Liners", VELLING, "Long", "Aloe",
            counts((20, 1.6), (40, 2.9), (60, 3.9)), "Flexible liners that bend with the body, sold loose in a value box.", TEAL),
    _liners("HFLXUN", "Extra Long Unscented Panty Liners", QUELLMOOR, "Extra Long", "Unscented",
            counts((16, 1.5), (32, 2.75)), "Wide, quilted liners with a cotton top sheet, sealed one by one in film.", PURPLE),
)  # fmt: skip

#: Text-match decoys: the title names a range holding the query's word, the fields say another
#: length or scent, so only a policy that reads ``liner_length`` or ``scent`` puts the real packs
#: first.
DECOYS = (
    Decoy(6, "long panty liners", "generic", decoy(
        ROWS[0], "HFLDY1", "Long Weekend Regular Unscented Panty Liners",
        "From the Long Weekend range: thin, flexible liners, each one folded in its own wrapper.")),
    Decoy(6, "fresh scent panty liners", "generic", decoy(
        ROWS[1], "HFLDY2", "Fresh Start Long Unscented Panty Liners",
        "From the Fresh Start range: liners with a breathable back and a soft top.")),
)  # fmt: skip

SPEC = TypeSpec(
    key="panty_liners",
    department="Health",
    product_type="Panty Liners",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=DECOYS,
)
