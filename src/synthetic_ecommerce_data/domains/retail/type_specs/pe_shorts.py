"""PE Shorts (gen#205): Kids shorts for PE by leg, fabric and pack.

:mod:`kit_school` draws the leg a style states; a pack is what a style is sold as, so
:mod:`pack_copies` lays out that many pairs. The styles are templates only (``derivable`` False).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import details
from synthetic_ecommerce_data.domains.retail.school_rows import (
    _BASE,
    _BRANDS,
    BLACK,
    BLUE,
    BW,
    CL,
    GREEN,
    LF,
    LK,
    NAVY,
    RED,
    WHITE,
    _a,
    _pack,
    _row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import (
    BRAND_OWNER,
    ApparelPlan,
    Row,
    TypeSpec,
    cw,
)

details.register_parts("pe_shorts", {"waistband": details.WAIST})

_SHORTS = (*_BASE, "PE Shorts")
YELLOW = cw("Yellow", "#e6c34a")


def _shorts(code, title, brand, leg, fabric, pack, price, desc, colors) -> Row:
    return _row(code, title, brand, _SHORTS, "PE Shorts", price, "pe_shorts", desc, colors,
                (_a("leg_length", "Leg length", leg), _a("fabric", "Fabric", fabric),
                 _a("pack_size", "Pack size", _pack(pack))), (("leg", leg.lower()),))  # fmt: skip


SPEC = TypeSpec(
    key="pe_shorts",
    department="Clothing",
    product_type="PE Shorts",
    owners=tuple((b, BRAND_OWNER[b]) for b in _BRANDS),
    rows=(
        _shorts("SPESH1", "Short Leg PE Shorts", LF, "Short", "Polyester", 1, 4.0,
                "Light PE shorts with an elastic waist and a short leg.",
                (BLACK, NAVY, WHITE, RED)),
        _shorts("SPESH2", "Short Leg PE Shorts, 2 Pack", CL, "Short", "Polyester", 2, 7.0,
                "Two pairs of PE shorts with an elastic waist, one for the bag and one for the wash.",
                (BLACK, NAVY, GREEN, BLUE)),
        _shorts("SPEMD1", "Mid Length PE Shorts", BW, "Mid", "Mesh", 1, 5.0,
                "Breathable mesh PE shorts cut to the mid thigh with an elastic waist.",
                (BLACK, NAVY, YELLOW)),
        _shorts("SPEMD2", "Mid Length PE Shorts, 2 Pack", LK, "Mid", "Cotton", 2, 9.0,
                "Two pairs of soft cotton PE shorts cut to the mid thigh.", (BLACK, NAVY)),
    ),
    apparel=ApparelPlan(
        compounds=(("football", "Football PE Shorts"), ("gym", "Gym PE Shorts"),
                   ("training", "Training PE Shorts")),
    ),
)  # fmt: skip
