"""School Polo Shirt (gen#205): Kids school polos by sleeve, fabric and pack.

:mod:`kit_school` draws them; a pack is what a style is sold as, so :mod:`pack_copies` lays out
that many polos. The styles are templates only (``derivable`` False).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import details
from synthetic_ecommerce_data.domains.retail.school_rows import (
    _BASE,
    _BRANDS,
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

details.register_parts("school_polo", {"hem": details.TORSO_HEM, "collar": details.COLLAR})

_POLOS = (*_BASE, "School Polo Shirts")
YELLOW = cw("Yellow", "#e6c34a")


def _polo(code, title, brand, sleeve, fabric, pack, price, desc, colors) -> Row:
    return _row(code, title, brand, _POLOS, "School Polo Shirt", price, "school_polo", desc, colors,
                (_a("sleeve_length", "Sleeve length", sleeve), _a("fabric", "Fabric", fabric),
                 _a("pack_size", "Pack size", _pack(pack))), (("sleeve", sleeve.lower()),))  # fmt: skip


SPEC = TypeSpec(
    key="school_polo",
    department="Clothing",
    product_type="School Polo Shirt",
    owners=tuple((b, BRAND_OWNER[b]) for b in _BRANDS),
    rows=(
        _polo("SCPSS1", "Short Sleeve School Polo Shirt", LF, "Short", "Cotton", 1, 5.0,
              "A short sleeve school polo with a ribbed collar and a two-button placket.",
              (WHITE, NAVY, RED)),
        _polo("SCPSS2", "Short Sleeve School Polo Shirt, 2 Pack", CL, "Short", "Polyester Cotton", 2,
              8.0, "Two short sleeve school polos with a ribbed collar, a pair for the week.",
              (WHITE, NAVY, GREEN)),
        _polo("SCPSS3", "Short Sleeve School Polo Shirt, 3 Pack", BW, "Short", "Polyester Cotton", 3,
              11.0, "Three short sleeve school polos with ribbed cuffs and a split hem.",
              (WHITE, BLUE, YELLOW)),
        _polo("SCPLS1", "Long Sleeve School Polo Shirt", LK, "Long", "Cotton", 1, 6.5,
              "A long sleeve school polo with ribbed cuffs for the colder terms.", (WHITE, NAVY)),
        _polo("SCPLS2", "Long Sleeve School Polo Shirt, 2 Pack", LF, "Long", "Polyester Cotton", 2,
              11.0, "Two long sleeve school polos with a ribbed collar and ribbed cuffs.",
              (WHITE, RED, BLUE)),
    ),
    apparel=ApparelPlan(
        compounds=(("pique", "Pique School Polo Shirt"), ("sports", "Sports School Polo Shirt"),
                   ("zip", "Zip Neck School Polo Shirt")),
    ),
)  # fmt: skip
