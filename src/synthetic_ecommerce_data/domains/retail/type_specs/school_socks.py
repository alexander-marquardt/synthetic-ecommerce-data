"""School Socks (gen#205): Kids ankle socks, knee-high socks and tights by UK shoe size band.

:mod:`kit_school` draws the height a style states; a pack fans as :mod:`pack_copies` fans socks.
``class_rows_apparel`` holds one more style in this leaf (``PLT-SK5KID``, of type Socks, which the
real-classes proof names). The styles are templates only (``derivable`` False).
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
    DEPARTMENT,
    GREY,
    LF,
    LK,
    NAVY,
    WHITE,
    _a,
    _pack,
)
from synthetic_ecommerce_data.domains.retail.size_ladder import SOCK_BANDS
from synthetic_ecommerce_data.domains.retail.type_registry import (
    BRAND_OWNER,
    ApparelPlan,
    Option,
    Row,
    TypeSpec,
)

details.register_parts(
    "school_socks", {"heel": details.sock_part("_HEEL"), "toe": details.sock_part("_TOE")}
)

_SOCKS = (*_BASE, "School Socks")
_HEIGHT = {"Ankle": "ankle", "Knee High": "knee", "Tights": "tights"}


def _sock(code, title, brand, style, fabric, pack, price, desc, colors) -> Row:
    sizes = tuple((band, round(price + 0.5 * i, 2)) for i, band in enumerate(SOCK_BANDS))
    return Row(code, title, brand, DEPARTMENT, _SOCKS, "School Socks", price, "school_socks", desc,
               colors, (_a("sock_style", "Sock style", style), _a("fabric", "Fabric", fabric),
                        _a("pack_size", "Pack size", _pack(pack))),
               sizes, audience="kids", size_key="shoe_size_band",
               params=(("height", _HEIGHT[style]),))  # fmt: skip


SPEC = TypeSpec(
    key="school_socks",
    department="Clothing",
    product_type="School Socks",
    owners=tuple((b, BRAND_OWNER[b]) for b in _BRANDS),
    options=(Option("shoe_size_band", "shoe_size_band", "Shoe size band"),),
    rows=(
        _sock("SCSAN5", "Ankle School Socks, 5 Pack", LF, "Ankle", "Cotton", 5, 6.0,
              "Five pairs of ankle school socks with a ribbed cuff.", (WHITE, GREY, BLACK, NAVY)),
        _sock("SCSAN7", "Ankle School Socks, 7 Pack", CL, "Ankle", "Cotton", 7, 8.0,
              "Seven pairs of ankle school socks, one for each day of the week.",
              (WHITE, GREY, BLACK)),
        _sock("SCSKN3", "Knee High School Socks, 3 Pack", BW, "Knee High", "Cotton", 3, 6.0,
              "Three pairs of knee-high school socks that stay up all day.",
              (WHITE, GREY, NAVY)),
        _sock("SCSKN5", "Knee High School Socks, 5 Pack", LK, "Knee High", "Polyester", 5, 9.0,
              "Five pairs of knee-high school socks with a ribbed cuff.", (GREY, BLACK, NAVY)),
        _sock("SCSTT3", "School Tights, 3 Pack", LF, "Tights", "Cotton", 3, 9.0,
              "Three pairs of opaque school tights with a ribbed waistband.", (BLACK, GREY, NAVY)),
    ),
    apparel=ApparelPlan(
        family="k",
        compounds=(("trainer", "Trainer School Socks"), ("frill", "Frill School Socks"),
                   ("bamboo", "Bamboo School Socks")),
    ),
)  # fmt: skip
