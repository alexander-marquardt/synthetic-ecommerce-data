"""Belt Bag (gen#1114): crescent, box and pouch bags worn on a belt.

**Womens > Accessories > Bags > Belt Bags**, a breadth type: the scaled build derives styles that swap the
material; the form, the closure and the belt stay the template's. One size, so a SKU is a color.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import bags_common as bc
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec

PT = "Belt Bag"


def _row(code, title, brand, price, desc, colors, form, material, closure, strap):
    return bc.bag_row(code, title, brand, price, desc, colors, PT, "belt_bag", form, material, closure, strap)


_ROWS = (
    _row("BLBCRN", "Nylon Crescent Belt Bag", bc.WRENFIELD, 18.0,
         "A light nylon bag for the waist, with a curved zip top and a hidden pocket at the back.",
         bc.SOFT, "Crescent", "Nylon", "Zip", "Adjustable"),
    _row("BLBCRL", "Leather Crescent Belt Bag", bc.CALDERBY, 48.0,
         "A curved leather bag for the waist, with a zip top and a lined interior.",
         bc.CLASSIC, "Crescent", "Leather", "Zip", "Adjustable"),
    _row("BLBBXC", "Canvas Box Belt Bag", bc.HARBOUR, 22.0,
         "A square canvas bag for the waist, with a zipped main pocket and a zipped front pocket.",
         bc.EARTH, "Box", "Canvas", "Zip", "Adjustable"),
    _row("BLBPCF", "Faux Leather Pouch Belt Bag", bc.THISTLE, 24.0,
         "A faux leather bag for the waist, with a flap, a stud and room for a phone and keys.",
         bc.BRIGHT, "Pouch", "Faux Leather", "Flap", "Adjustable"),
)  # fmt: skip

SPEC = TypeSpec(
    key="belt_bag",
    department=bc.DEPARTMENT,
    product_type=PT,
    rows=_ROWS,
    derivable=True,
    apparel_exempt=bc.APPAREL_EXEMPT,
    decoys=(
        bc.decoy(1, "red belt bag", "color", _row(
            "BLBDRD", "Belt Bag with Red Strap", bc.WRENFIELD, 19.0,
            "A black nylon bag for the waist, with a red strap and a stud flap.", (bc.BLACK,), "Pouch", "Nylon", "Flap", "Adjustable")),
        bc.decoy(4, "leather belt bag", "generic", _row(
            "BLBDLK", "Faux Leather Crescent Belt Bag", bc.THISTLE, 21.0,
            "A curved faux leather bag for the waist; there is no leather in it.", (bc.TAN,), "Crescent", "Faux Leather", "Zip", "Adjustable")),
        bc.decoy(6, "white belt bag", "color", _row(
            "BLBDWH", "White Cliffs Belt Bag", bc.CALDERBY, 26.0,
            "From the White Cliffs range: a square bag for the waist with a zipped front pocket.", (bc.NAVY,), "Box", "Canvas", "Zip", "Adjustable")),
    ),
)  # fmt: skip
