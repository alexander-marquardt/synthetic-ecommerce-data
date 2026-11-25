"""Messenger Bag (gen#1114): men's courier, satchel and utility bags on a wide strap.

**Mens > Accessories > Bags > Messenger Bags**, a breadth type: the scaled build derives styles that swap the
material; the form, the closure and the strap stay the template's. A SKU is a color times a capacity in
liters.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import bags_common as bc
from synthetic_ecommerce_data.domains.retail.audience import MENS
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec

PT = "Messenger Bag"


def _row(code, title, brand, price, desc, colors, form, material, closure, strap):
    return bc.bag_row(code, title, brand, price, desc, colors, PT, "messenger_bag", form, material, closure, strap,
                      (("10", price), ("15", price + 9)), MENS, "capacity_l")  # fmt: skip


_ROWS = (
    _row("MSGCRC", "Canvas Courier Messenger Bag", bc.HARBOUR, 38.0,
         "A hard-wearing canvas bag with a deep flap, two quick-release clips and a padded shoulder strap.",
         bc.EARTH, "Courier", "Canvas", "Flap", "Adjustable"),
    _row("MSGCRN", "Nylon Courier Messenger Bag", bc.WRENFIELD, 32.0,
         "A nylon bag with a deep flap, two quick-release clips and a pocket for a bottle.",
         bc.BRIGHT, "Courier", "Nylon", "Flap", "Adjustable"),
    _row("MSGSTL", "Leather Satchel Messenger Bag", bc.CALDERBY, 98.0,
         "A leather bag with a rounded flap, a metal lock and a lined main pocket.",
         bc.CLASSIC, "Satchel", "Leather", "Flap", "Adjustable"),
    _row("MSGUTF", "Faux Leather Utility Messenger Bag", bc.THISTLE, 44.0,
         "A faux leather bag with two stud pockets on the front and a short flap over the main pocket.",
         bc.SOFT, "Utility", "Faux Leather", "Flap", "Adjustable"),
)  # fmt: skip

SPEC = TypeSpec(
    key="messenger_bag",
    department=bc.DEPARTMENT,
    product_type=PT,
    rows=_ROWS,
    derivable=True,
    apparel_exempt=bc.APPAREL_EXEMPT,
    decoys=(
        bc.decoy(1, "red messenger bag", "color", _row(
            "MSGDRD", "Messenger Bag with Red Strap", bc.WRENFIELD, 34.0,
            "A black nylon bag with a red strap and a deep flap.", (bc.BLACK,), "Courier", "Nylon", "Flap", "Adjustable")),
        bc.decoy(4, "leather messenger bag", "generic", _row(
            "MSGDLK", "Faux Leather Satchel Messenger Bag", bc.THISTLE, 42.0,
            "A bag with a rounded flap in faux leather; there is no leather in it.", (bc.TAN,), "Satchel", "Faux Leather", "Flap", "Adjustable")),
        bc.decoy(6, "blue messenger bag", "color", _row(
            "MSGDBL", "Blue Hour Messenger Bag", bc.HARBOUR, 40.0,
            "From the Blue Hour range: a canvas bag with two stud pockets on the front.", (bc.KHAKI,), "Utility", "Canvas", "Flap", "Adjustable")),
    ),
)  # fmt: skip
