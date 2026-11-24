"""Clutch Bag (gen#1114): envelope, foldover and frame clutches for evenings.

**Womens > Accessories > Bags > Clutch Bags**, a breadth type: the scaled build derives styles
that swap the material; the form and the closure stay the template's. A clutch has one size, so a
SKU is a color.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import bags_common as bc
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec

PT = "Clutch Bag"


def _row(code, title, brand, price, desc, colors, form, material, closure):
    return bc.bag_row(code, title, brand, price, desc, colors, PT, "clutch_bag", form, material, closure)


_ROWS = (
    _row("CLTENS", "Satin Envelope Clutch Bag for Evenings", bc.CALDERBY, 26.0,
         "A slim satin clutch with a pointed flap and a magnetic stud, for weddings and dinners.",
         bc.BRIGHT, "Envelope", "Satin", "Magnetic"),
    _row("CLTFOV", "Velvet Foldover Clutch Bag", bc.WRENFIELD, 24.0,
         "A soft velvet clutch whose zipped top folds down, with room for a phone and a lipstick.",
         bc.SOFT, "Foldover", "Velvet", "Zip"),
    _row("CLTFOF", "Faux Leather Foldover Clutch Bag", bc.HARBOUR, 25.0,
         "A soft faux leather clutch whose zipped top folds down, big enough for a purse.",
         bc.EARTH, "Foldover", "Faux Leather", "Zip"),
    _row("CLTFRV", "Velvet Frame Clutch Bag", bc.CALDERBY, 34.0,
         "A rounded velvet clutch on a metal frame that snaps shut with a kiss clasp.",
         bc.CLASSIC, "Frame", "Velvet", "Clasp"),
)  # fmt: skip

SPEC = TypeSpec(
    key="clutch_bag",
    department=bc.DEPARTMENT,
    product_type=PT,
    rows=_ROWS,
    derivable=True,
    apparel_exempt=bc.APPAREL_EXEMPT,
    decoys=(
        bc.decoy(1, "red clutch bag", "color", _row(
            "CLTDRD", "Contrast Lining Clutch Bag", bc.WRENFIELD, 21.0,
            "A black satin clutch with a red lining.", (bc.BLACK,), "Envelope", "Satin", "Magnetic")),
        bc.decoy(4, "satin clutch bag", "generic", _row(
            "CLTDST", "Satin-Finish Clutch Bag", bc.THISTLE, 20.0,
            "A clutch with a sheen like satin; it is faux leather through and through.", (bc.NAVY,), "Foldover", "Faux Leather", "Zip")),
        bc.decoy(6, "velvet clutch bag", "generic", _row(
            "CLTDVR", "Velvet Rope Clutch Bag", bc.CALDERBY, 29.0,
            "From the Velvet Rope range: a smooth clutch with a kiss clasp.", (bc.BLACK,), "Frame", "Satin", "Clasp")),
    ),
)  # fmt: skip
