"""Fabric (gen#1118, cut 1): Office & School > Sewing & Knitting > Fabric.

A breadth type: ``derivable`` True, so the scaled build draws more fabrics from these four by the
values their titles show (the fiber and the weave). A fabric is sold by the cut: a fat quarter
(about 50 x 55 cm, the quilter's cut), one meter or two meters off the bolt, each a
SKU of the ``fabric_cut`` option at its own price. The picture is the same folded fabric whatever
the cut (``size_axes.NOT_SIZES``). The drawing shows three folded layers with the weave on each
face and a sheen for a polyester (:func:`kit_sewing.fabric`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.office_rows import BLUE, CALDERBY, GREEN, decoy
from synthetic_ecommerce_data.domains.retail.sewing_rows import (
    BOBBINMERE,
    DEPARTMENT,
    FABRIC,
    OWNERS,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Option, TypeSpec, a


def _cuts(per_meter: float) -> tuple[tuple[str, float], ...]:
    """A fabric's cuts and the price of each: a fat quarter costs a little under half a meter's worth."""
    return (("Fat Quarter", round(per_meter * 0.45, 2)), ("1 Meter", per_meter),
            ("2 Meters", round(per_meter * 1.9, 2)))  # fmt: skip


def _row(code: str, material: str, style: str, brand: str, description: str, per_meter: float):
    attrs = (a("material", "Material", material), a("style", "Style", style))
    params = (("style", style.lower()), ("material", material.lower()))
    return row(code, f"{material} {style} Fabric", brand, FABRIC, "Fabric", "fabric", description, attrs,
               _cuts(per_meter), params, size_key="fabric_cut")  # fmt: skip


ROWS = (
    _row(
        "FABCPO",
        "Cotton",
        "Poplin",
        BOBBINMERE,
        "A crisp, closely woven fabric 145 cm wide, for shirts, dresses and quilting, washable at 40 degrees.",
        11.0,
    ),
    _row(
        "FABCCA",
        "Cotton",
        "Canvas",
        CALDERBY,
        "A heavy, hard-wearing fabric 140 cm wide, for bags, cushions, aprons and upholstery.",
        16.0,
    ),
    _row(
        "FABPCR",
        "Polyester",
        "Crepe",
        CALDERBY,
        "A light, fluid fabric 150 cm wide with a fine crinkled face that drapes well, for blouses and skirts.",
        9.0,
    ),
    _row(
        "FABPJE",
        "Polyester",
        "Jersey",
        BOBBINMERE,
        "A soft, stretchy knit fabric 150 cm wide, for T-shirts, leggings and loungewear.",
        12.0,
    ),
)

SPEC = TypeSpec(
    key="fabric",
    department=DEPARTMENT,
    product_type="Fabric",
    derivable=True,
    owners=OWNERS,
    options=(Option("fabric_cut", "fabric_cut", "Fabric cut"),),
    rows=ROWS,
    decoys=(
        Decoy(4, "yellow fabric", "vocabulary", decoy(ROWS[0], "FABYSV", "Cotton Poplin Fabric with a Yellow Selvage",
              "A blue cotton poplin whose selvage is printed with the maker's name.", BLUE)),
        Decoy(6, "red fabric", "generic", decoy(ROWS[1], "FABRRB", "Red Robin Cotton Canvas Fabric",
              "From the Red Robin range: a heavy cotton canvas in a leaf green.", GREEN)),
    ),
)  # fmt: skip
