"""Laptop Bag (gen#1114): men's briefcase, top load and folio bags for a laptop.

**Mens > Accessories > Bags > Laptop Bags**, a breadth type: the scaled build derives styles that swap the
material; the form and the closure stay the template's. A SKU is a color times the screen size the
bag holds, in inches.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import bags_common as bc
from synthetic_ecommerce_data.domains.retail.audience import MENS
from synthetic_ecommerce_data.domains.retail.type_registry import Option, TypeSpec

PT = "Laptop Bag"


def _row(code, title, brand, price, desc, colors, form, material, closure):
    return bc.bag_row(code, title, brand, price, desc, colors, PT, "laptop_bag", form, material, closure, None,
                      (("13", price), ("14", price + 3), ("16", price + 6)), MENS, "screen_size_in")  # fmt: skip


_ROWS = (
    _row("LPBBRL", "Leather Briefcase Laptop Bag", bc.CALDERBY, 110.0,
         "A leather bag with two handles, a padded laptop pocket and a zipped front pocket.",
         bc.CLASSIC, "Briefcase", "Leather", "Zip"),
    _row("LPBTLN", "Nylon Top Load Laptop Bag", bc.WRENFIELD, 29.0,
         "A nylon bag with a flat handle, a padded laptop pocket and a flap pocket for a charger.",
         bc.SOFT, "Top Load", "Nylon", "Zip"),
    _row("LPBTLC", "Canvas Top Load Laptop Bag", bc.HARBOUR, 42.0,
         "A sturdy canvas bag with a flat handle, a padded laptop pocket and a flap pocket for papers.",
         bc.EARTH, "Top Load", "Canvas", "Zip"),
    _row("LPBFLF", "Faux Leather Folio Laptop Bag", bc.THISTLE, 35.0,
         "A slim faux leather bag that zips round three sides, with a padded laptop pocket and a pen loop.",
         bc.BRIGHT, "Folio", "Faux Leather", "Zip"),
)  # fmt: skip

SPEC = TypeSpec(
    key="laptop_bag",
    department=bc.DEPARTMENT,
    product_type=PT,
    options=(Option("screen_size_in", "screen_size", "Screen size", "INH"),),
    rows=_ROWS,
    derivable=True,
    apparel_exempt=bc.APPAREL_EXEMPT,
    decoys=(
        bc.decoy(1, "red laptop bag", "color", _row(
            "LPBDRD", "Contrast Lining Laptop Bag", bc.WRENFIELD, 33.0,
            "A black nylon bag for a laptop, with a red lining.", (bc.BLACK,), "Top Load", "Nylon", "Zip")),
        bc.decoy(4, "leather laptop bag", "generic", _row(
            "LPBDLK", "Faux Leather Briefcase Laptop Bag", bc.THISTLE, 45.0,
            "A bag with two handles in faux leather; there is no leather in it.", (bc.TAN,), "Briefcase", "Faux Leather", "Zip")),
        bc.decoy(6, "green laptop bag", "color", _row(
            "LPBDGR", "Green Light Laptop Bag", bc.CALDERBY, 52.0,
            "From the Green Light range: a slim bag that zips round three sides.", (bc.NAVY,), "Folio", "Canvas", "Zip")),
    ),
)  # fmt: skip
