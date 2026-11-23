"""Watch Strap (gen#1113): a replacement strap, sold by color and by lug width.

It sits beside the watches of its audience, in Womens and in Mens. A SKU is a strap color times a
lug width in millimetres (``lug_mm``, a measured option). ``material`` is drawn by
:mod:`kit_jewellery` (leather, silicone, fabric or mesh). A mesh strap is metal, so its colors are
metals; the other straps carry the six main colors (gen#275) between the styles of each audience.
The rows are derivable, and a derived style keeps its template's strap
(``scale_text.JEWELLERY_KEYS``).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.audience import MENS, WOMENS
from synthetic_ecommerce_data.domains.retail.breadth_rows import Row
from synthetic_ecommerce_data.domains.retail.jewellery_rows import (
    BLACK,
    BLUE,
    BROWN,
    CALDERBY,
    CLOTHING,
    GOLD,
    GREEN,
    HARBOUR,
    LARKMOOR,
    MAIN_SIX,
    OWNED,
    RED,
    ROSE_GOLD,
    SILVER,
    SKERRY,
    TIDEWELL,
    WRENFIELD,
    a,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Option, TypeSpec

PTYPE = "Watch Strap"
WOMENS_MM, MENS_MM = ("14", "16", "18"), ("18", "20", "22")
STRAPS = {"leather": "Leather", "silicone": "Silicone", "fabric": "Fabric", "mesh": "Stainless Steel Mesh"}


def _row(code, title, brand, who, price, desc, material, colors):
    sizes = tuple((mm, price) for mm in (WOMENS_MM if who == WOMENS else MENS_MM))
    attrs = (
        a("strap", "Strap", STRAPS[material]),
        a("strap_fastening", "Strap fastening", "Slide Clasp" if material == "mesh" else "Pin Buckle"),
        a("audience", "Audience", who),
    )  # fmt: skip
    return Row(code, title, brand, CLOTHING, (who, "Watches", "Watch Straps"), PTYPE, price, "watch_strap", desc,
               colors, attrs, sizes, size_key="lug_mm", params=(("material", material),))  # fmt: skip


SPEC = TypeSpec(
    key="watch_strap",
    department="Clothing",
    product_type=PTYPE,
    derivable=True,
    options=(Option("lug_mm", "lug_width", "Lug width", "MMT"),),
    owners=OWNED,
    apparel_exempt="a watch strap: the color is the strap material, not a printed or dyed garment color; it carries its own decoys (gen#1113)",
    rows=(
        _row("WSTWLE", "Womens Leather Watch Strap", WRENFIELD, WOMENS, 14.0,
             "A slim leather watch strap with a stitched edge and a pin buckle, with quick release bars.",
             "leather", (BLACK, BROWN, BLUE, RED)),
        _row("WSTWSI", "Womens Silicone Watch Strap", TIDEWELL, WOMENS, 10.0,
             "A soft ribbed silicone watch strap with a pin buckle, easy to wipe clean.",
             "silicone", MAIN_SIX),
        _row("WSTWFB", "Womens Woven Fabric Watch Strap", HARBOUR, WOMENS, 11.0,
             "A light woven fabric watch strap with a center stripe and a pin buckle.",
             "fabric", (BLACK, BLUE, GREEN, RED)),
        _row("WSTWMS", "Womens Mesh Watch Strap", SKERRY, WOMENS, 18.0,
             "A fine steel mesh watch strap with a slide clasp that fits any wrist.",
             "mesh", (GOLD, SILVER, ROSE_GOLD)),
        _row("WSTMLE", "Mens Leather Watch Strap", CALDERBY, MENS, 17.0,
             "A padded leather watch strap with a stitched edge and a pin buckle, with quick release bars.",
             "leather", (BLACK, BROWN, BLUE, GREEN)),
        _row("WSTMSI", "Mens Silicone Watch Strap", LARKMOOR, MENS, 12.0,
             "A ribbed silicone watch strap with a pin buckle, for swimming and training.",
             "silicone", MAIN_SIX),
        _row("WSTMFB", "Mens Woven Fabric Watch Strap", TIDEWELL, MENS, 12.0,
             "A tough woven fabric watch strap with a center stripe and a pin buckle.",
             "fabric", (BLACK, BLUE, GREEN, RED)),
        _row("WSTMMS", "Mens Mesh Watch Strap", WRENFIELD, MENS, 21.0,
             "A steel mesh watch strap with a slide clasp that fits any wrist.",
             "mesh", (SILVER, GOLD, BLACK)),
    ),
    decoys=(
        Decoy(5, "black leather watch strap", "color",
              _row("WSTDBK", "Stitched Replacement Strap", SKERRY, MENS, 15.0,
                   "A brown leather watch strap with a black stitched edge: the strap itself is brown.",
                   "leather", (BROWN,))),
        Decoy(4, "leather watch strap", "material",
              _row("WSTDLL", "Grained Replacement Strap", LARKMOOR, WOMENS, 9.0,
                   "A silicone watch strap with a leather look grain: soft silicone, not leather.",
                   "silicone", (BLACK,))),
    ),
)  # fmt: skip
