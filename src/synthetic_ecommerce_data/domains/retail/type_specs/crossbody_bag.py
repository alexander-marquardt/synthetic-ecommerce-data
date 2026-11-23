"""Crossbody Bag (gen#1114): saddle, camera and satchel bags on a long strap.

**Womens > Accessories > Bags > Crossbody Bags**, a breadth type: the scaled build derives styles
that swap the material; the form, the closure and the strap stay the template's. A SKU is a color
times a size (Small or Medium).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import bags_common as bc
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec

PT = "Crossbody Bag"


def _row(code, title, brand, price, desc, colors, form, material, closure, strap):
    return bc.bag_row(code, title, brand, price, desc, colors, PT, "crossbody_bag", form, material, closure, strap,
                      bc.small_medium(price, price + 8))  # fmt: skip


_ROWS = (
    _row("CBGSDL", "Leather Saddle Crossbody Bag", bc.CALDERBY, 56.0,
         "A rounded leather crossbody with a stud flap, a lined interior and a zipped inner pocket.",
         bc.CLASSIC, "Saddle", "Leather", "Flap", "Adjustable"),
    _row("CBGSDC", "Canvas Saddle Crossbody Bag", bc.HARBOUR, 26.0,
         "A light canvas crossbody with a stud flap and a slip pocket at the back for a phone.",
         bc.EARTH, "Saddle", "Canvas", "Flap", "Adjustable"),
    _row("CBGCMN", "Nylon Camera Crossbody Bag", bc.WRENFIELD, 22.0,
         "A wipe-clean nylon crossbody with a zip top, a zipped front pocket and a wide strap.",
         bc.SOFT, "Camera", "Nylon", "Zip", "Adjustable"),
    _row("CBGSTF", "Faux Leather Satchel Crossbody Bag", bc.THISTLE, 34.0,
         "A structured faux leather crossbody with two buckled straps and a slip pocket at the back.",
         bc.BRIGHT, "Satchel", "Faux Leather", "Buckle", "Adjustable"),
)  # fmt: skip

SPEC = TypeSpec(
    key="crossbody_bag",
    department=bc.DEPARTMENT,
    product_type=PT,
    rows=_ROWS,
    derivable=True,
    apparel_exempt=bc.APPAREL_EXEMPT,
    decoys=(
        bc.decoy(1, "red crossbody bag", "color", _row(
            "CBGDRD", "Crossbody Bag with Red Strap", bc.WRENFIELD, 27.0,
            "A black nylon crossbody with a red strap and a zip top.", (bc.BLACK,), "Camera", "Nylon", "Zip", "Adjustable")),
        bc.decoy(4, "leather crossbody bag", "generic", _row(
            "CBGDLK", "Leather-Look Crossbody Bag", bc.THISTLE, 25.0,
            "A crossbody with a leather-look finish; there is no leather in it.", (bc.TAN,), "Saddle", "Faux Leather", "Flap", "Adjustable")),
        bc.decoy(6, "canvas crossbody bag", "generic", _row(
            "CBGDCN", "Blank Canvas Crossbody Bag", bc.CALDERBY, 38.0,
            "From the Blank Canvas range: a smooth crossbody with a zip top.", (bc.WHITE,), "Camera", "Nylon", "Zip", "Adjustable")),
    ),
)  # fmt: skip
