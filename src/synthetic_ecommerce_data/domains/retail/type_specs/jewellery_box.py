"""Jewellery Box (gen#1113): a box to keep jewelry in, sold by color.

It sits under ``Jewellery`` as ``Jewellery Boxes``. Each SKU is a color of the box's covering; the
six main colors (gen#275) are spread over the styles. ``style`` is drawn by :mod:`kit_jewellery`
(a closed case, a mirror lid open over ring rolls, a chest of drawers, a zipped travel case), and
``mirror`` is Yes on the style that draws one. The rows are derivable, and a derived style keeps
its template's style, material, compartments, mirror and lock (``scale_text.JEWELLERY_KEYS``).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.audience import WOMENS
from synthetic_ecommerce_data.domains.retail.breadth_row import Row
from synthetic_ecommerce_data.domains.retail.jewellery_rows import (
    BLACK,
    BLUE,
    BROWN,
    CALDERBY,
    CLOTHING,
    GREEN,
    HARBOUR,
    LARKMOOR,
    OWNED,
    RED,
    SKERRY,
    TIDEWELL,
    WHITE,
    WRENFIELD,
    YELLOW,
    a,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec

PATH, PTYPE = ("Womens", "Jewellery", "Jewellery Boxes"), "Jewellery Box"
STYLES = {"case": "Case", "mirror": "Mirror Lid", "drawers": "Drawers", "travel": "Travel Case"}


def _row(code, title, brand, price, desc, style, material, compartments, colors, lock=False):
    attrs = (
        a("box_style", "Box style", STYLES[style]), a("material", "Material", material),
        ("compartments", "Compartments", str(compartments), "C62"), a("mirror", "Mirror", "Yes" if style == "mirror" else "No"),
        a("lock", "Lock", "Yes" if lock else "No"), a("audience", "Audience", WOMENS),
    )  # fmt: skip
    return Row(code, title, brand, CLOTHING, PATH, PTYPE, price, "jewellery_box", desc, colors, attrs,
               params=(("style", style),))  # fmt: skip


SPEC = TypeSpec(
    key="jewellery_box",
    department="Clothing",
    product_type=PTYPE,
    derivable=True,
    owners=OWNED,
    apparel_exempt="a jewelry box: the color is the covering of a box, not a printed or dyed garment color; it carries its own decoys (gen#1113)",
    rows=(
        _row("JBXMIR", "Mirror Lid Jewellery Box", WRENFIELD, 32.0,
             "A jewelry box in stitched faux leather with a mirror in the lid, ring rolls and eight compartments.",
             "mirror", "Faux Leather", 8, (BLACK, WHITE, RED)),
        _row("JBXMRV", "Velvet Mirror Jewellery Box", LARKMOOR, 28.0,
             "A soft velvet jewelry box with a mirror in the lid, ring rolls and six compartments.",
             "mirror", "Velvet", 6, (BLUE, GREEN)),
        _row("JBXDRW", "Two Drawer Jewellery Box", CALDERBY, 45.0,
             "A faux leather jewelry box with a lift up lid, two lined drawers and a lock and key: twelve compartments in all.",
             "drawers", "Faux Leather", 12, (BLACK, WHITE, YELLOW), lock=True),
        _row("JBXDRB", "Wooden Jewellery Box with Drawers", HARBOUR, 55.0,
             "A wooden jewelry box with a lid and two lined drawers, ten compartments in all.",
             "drawers", "Wood", 10, (BROWN, BLACK)),
        _row("JBXCAS", "Small Jewellery Case", HARBOUR, 18.0,
             "A small faux leather jewelry case with a press clasp and four lined compartments.",
             "case", "Faux Leather", 4, (RED, BLUE, YELLOW)),
        _row("JBXRNG", "Velvet Ring Box", SKERRY, 9.0,
             "A small velvet ring box with one ring slot, for a gift or a proposal.",
             "case", "Velvet", 1, (RED, BLUE, GREEN)),
        _row("JBXTRV", "Zip Travel Jewellery Case", TIDEWELL, 16.0,
             "A zipped faux leather travel jewelry case with ring rolls and five compartments.",
             "travel", "Faux Leather", 5, (BLACK, BLUE, GREEN)),
        _row("JBXTRQ", "Quilted Travel Jewellery Case", SKERRY, 14.0,
             "A quilted cotton travel jewelry case with a zip and four compartments.",
             "travel", "Quilted Cotton", 4, (WHITE, YELLOW, RED)),
    ),
    decoys=(
        Decoy(5, "white jewellery box", "color",
              _row("JBXDWS", "Black Jewellery Box, White Contrast Lining", WRENFIELD, 26.0,
                   "A black faux leather jewelry box with white contrast stitching and a mirror in the lid: the box itself is black.",
                   "mirror", "Faux Leather", 6, (BLACK,))),
        Decoy(4, "earrings", "category",
              _row("JBXDER", "Earring Organizer Box", LARKMOOR, 19.0,
                   "A jewelry box with rows of slots that hold forty pairs of earrings: a box to keep them in, earrings not included.",
                   "case", "Faux Leather", 40, (WHITE,))),
    ),
)  # fmt: skip
