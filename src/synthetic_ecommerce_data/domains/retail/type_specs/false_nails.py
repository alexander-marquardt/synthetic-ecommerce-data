"""False nails (gen#751): tip shape and length are attributes, the color and the pack count are the SKU.

The other meaning of ``nails``: the hardware nails are under ``Fasteners > Nails`` in the
industrial catalog (:mod:`synthetic_ecommerce_data.domains.industrial.nails`). The styles are
templates only: the range grows by authored rows.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_beauty,  # noqa: F401 -- registers the false_nails shape
)
from synthetic_ecommerce_data.domains.retail.beauty_depth import D, decoy
from synthetic_ecommerce_data.domains.retail.breadth_rows import Row
from synthetic_ecommerce_data.domains.retail.main_color_hex import MAIN_COLORS
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a
from synthetic_ecommerce_data.domains.retail.variants import cw

RED, BLUE, GREEN, YELLOW, BLACK, WHITE = (cw(name, MAIN_COLORS[name]) for name in ("Red", "Blue", "Green", "Yellow", "Black", "White"))
PATH = (D, "Nails", "False Nails")


def _row(code, title, brand, price, desc, tip, length, colors) -> Row:
    """One style, sold in a small and a large pack."""
    return Row(code, title, brand, D, PATH, "False Nails", price, "false_nails", desc, colors,
               (a("tip_shape", "Tip shape", tip), a("nail_length", "Nail length", length)),
               (("24", price), ("30", round(price * 1.2, 2))), size_key="units_per_pack",
               params=(("tip", tip.lower()),))  # fmt: skip


ROWS = (
    _row("FNLALM", "Almond Press-On Nails", "Pearlbrook", 8.0,
        "Fake nails in a soft almond shape that press on with the glue tabs in the box.",
        "Almond", "Medium", (RED, BLUE)),
    _row("FNLCOF", "Coffin Press-On Nails", "Veilmoor", 9.0,
        "Long fake nails with a flat, tapered tip, in a gloss finish.",
        "Coffin", "Long", (BLACK, RED)),
    _row("FNLSQR", "Short Square Press-On Nails", "Aldermist", 7.0,
        "Short false nails with a straight tip that stay out of the way at work.",
        "Square", "Short", (WHITE, BLUE)),
    _row("FNLSTL", "Stiletto False Nails", "Veilmoor", 10.0,
        "Long false nails that taper to a point, with glue for a two-week wear.",
        "Stiletto", "Long", (GREEN, BLACK)),
    _row("FNLOVL", "Oval False Nail Set", "Aldermist", 7.5,
        "A set of short false nails with a rounded tip, and a file for each nail.",
        "Oval", "Short", (YELLOW, WHITE)),
)  # fmt: skip

SPEC = TypeSpec(
    key="false_nails",
    department="Beauty",
    product_type="False Nails",
    rows=ROWS,
    decoys=(
        Decoy(1, "pink press on nails", "color", decoy("FND1", "Pink Tray Press-On Nails", "Almond press-on nails in a pink tray.", ROWS[0])),
        Decoy(6, "green press on nails", "generic", decoy("FND2", "Green Valley Press-On Nails", "From the Green Valley range: coffin press-on nails.", ROWS[1])),
        Decoy(7, "red press on nails", "generic", decoy("FND3", "Press-On Nails", "Short square press-on nails.", ROWS[2], brand="Red Kestrel")),
    ),
    owners=(("Aldermist", "third_party"), ("Pearlbrook", "third_party"), ("Red Kestrel", "third_party"), ("Veilmoor", "third_party"),),
)  # fmt: skip
