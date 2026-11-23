"""Shoulder Bag (gen#1114): hobo, baguette and crescent bags carried under the arm.

**Womens > Accessories > Bags > Shoulder Bags**, a breadth type: the scaled build derives styles
that swap the material; the form and the closure stay the template's. A SKU is a color times a
size (Small or Medium).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import bags_common as bc
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec

PT = "Shoulder Bag"


def _row(code, title, brand, price, desc, colors, form, material, closure):
    return bc.bag_row(code, title, brand, price, desc, colors, PT, "shoulder_bag", form, material, closure, None,
                      bc.small_medium(price, price + 10))  # fmt: skip


_ROWS = (
    _row("SHBHBL", "Leather Hobo Shoulder Bag", bc.CALDERBY, 72.0,
         "A slouchy leather shoulder bag with an open top, a magnetic stud and room for a tablet.",
         bc.CLASSIC, "Hobo", "Leather", "Magnetic"),
    _row("SHBHBS", "Suede Hobo Shoulder Bag", bc.HARBOUR, 68.0,
         "A slouchy suede shoulder bag with a magnetic stud and a hanging inner pocket.",
         bc.EARTH, "Hobo", "Suede", "Magnetic"),
    _row("SHBBGF", "Faux Leather Baguette Shoulder Bag", bc.THISTLE, 32.0,
         "A long, low faux leather shoulder bag with a flap, a turn lock and a slim zipped pocket.",
         bc.BRIGHT, "Baguette", "Faux Leather", "Turn Lock"),
    _row("SHBCRS", "Suede Crescent Shoulder Bag", bc.THISTLE, 58.0,
         "A moon-shaped suede shoulder bag with a zip top and a tonal lining.",
         bc.SOFT, "Crescent", "Suede", "Zip"),
)  # fmt: skip

SPEC = TypeSpec(
    key="shoulder_bag",
    department=bc.DEPARTMENT,
    product_type=PT,
    rows=_ROWS,
    derivable=True,
    apparel_exempt=bc.APPAREL_EXEMPT,
    decoys=(
        bc.decoy(1, "red shoulder bag", "color", _row(
            "SHBDRD", "Contrast Lining Shoulder Bag", bc.WRENFIELD, 30.0,
            "A black faux leather shoulder bag with a red lining.", (bc.BLACK,), "Baguette", "Faux Leather", "Turn Lock")),
        bc.decoy(4, "suede shoulder bag", "generic", _row(
            "SHBDSU", "Suede-Look Shoulder Bag", bc.THISTLE, 27.0,
            "A shoulder bag with a brushed, suede-look finish; there is no suede in it.", (bc.TAN,), "Hobo", "Faux Leather", "Magnetic")),
        bc.decoy(6, "green shoulder bag", "color", _row(
            "SHBDGR", "Green Room Shoulder Bag", bc.CALDERBY, 70.0,
            "From the Green Room range: a structured shoulder bag with a flap.", (bc.NAVY,), "Baguette", "Leather", "Turn Lock")),
    ),
)  # fmt: skip
