"""School Blazer (gen#205): Kids blazers by fit, lining and whether a badge goes on.

:mod:`kit_school` draws the fit a style states and, on a badge-ready style, the outline of a
sewn-on badge on the chest pocket. The styles are templates only (``derivable`` False).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import details
from synthetic_ecommerce_data.domains.retail.school_rows import (
    _BASE,
    _BRANDS,
    BLACK,
    BW,
    CL,
    GREEN,
    GREY,
    LF,
    LK,
    NAVY,
    _a,
    _row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import (
    BRAND_OWNER,
    ApparelPlan,
    Row,
    TypeSpec,
    cw,
)

details.register_parts("school_blazer", {"hem": details.TORSO_HEM})

_BLAZERS = (*_BASE, "School Blazers")
BURGUNDY = cw("Burgundy", "#6b2337")
_FIT = {"Regular": "regular", "Slim": "slim", "Plus Fit": "plus"}


def _blazer(code, title, brand, fit, lining, badge_ready, fabric, price, desc, colors) -> Row:
    params = (("fit", _FIT[fit]), ("badge", "outline" if badge_ready == "Yes" else "none"))
    return _row(code, title, brand, _BLAZERS, "School Blazer", price, "school_blazer", desc, colors,
                (_a("fit", "Fit", fit), _a("lining", "Lining", lining),
                 _a("badge_ready", "Badge ready", badge_ready), _a("fabric", "Fabric", fabric)),
                params)  # fmt: skip


SPEC = TypeSpec(
    key="school_blazer",
    department="Clothing",
    product_type="School Blazer",
    owners=tuple((b, BRAND_OWNER[b]) for b in _BRANDS),
    rows=(
        _blazer("SCBREG", "Badge Ready School Blazer", LF, "Regular", "Half Lined", "Yes",
                "Viscose", 28.0,
                "A two-button school blazer with a chest pocket left plain for the school's badge.",
                (NAVY, BLACK, GREEN)),
        _blazer("SCBSLM", "Slim Fit School Blazer", CL, "Slim", "Fully Lined", "Yes",
                "Viscose", 32.0,
                "A slim fit two-button school blazer, fully lined, with a pocket ready for a badge.",
                (NAVY, BLACK, BURGUNDY)),
        _blazer("SCBPLN", "Plain School Blazer", BW, "Regular", "Half Lined", "No", "Wool",
                36.0, "A plain two-button school blazer in a wool blend, for a school with no badge.",
                (NAVY, GREY, BLACK)),
        _blazer("SCBPLS", "Plus Fit School Blazer", LK, "Plus Fit", "Fully Lined", "Yes",
                "Viscose", 34.0,
                "A roomier two-button school blazer with extra width through the chest and body.",
                (NAVY, BLACK)),
    ),
    apparel=ApparelPlan(
        compounds=(("wool", "Wool School Blazer"), ("stretch", "Stretch School Blazer"),
                   ("sixth", "Sixth Form School Blazer")),
    ),
)  # fmt: skip
