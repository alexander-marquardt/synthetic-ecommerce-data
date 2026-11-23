"""Yarn (gen#1118, cut 1): Office & School > Sewing & Knitting > Yarn.

A breadth type: ``derivable`` True, so the scaled build draws more yarns from these four by the
values their titles show (the weight and the fiber). The drawing is a ball of yarn in the SKU's
color, wound with a strand as thick as its weight, a fuzzy halo for a wool and a sheen for an
acrylic (:func:`kit_sewing.yarn`). The SKU is a color in a single ball or a pack of 5 or 10 (the
balls a sweater takes), which :mod:`pack_copies` draws as that many balls.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.office_rows import (
    BLUE,
    LANTERNBY,
    THISTLE,
    WHITE,
    decoy,
    packs,
)
from synthetic_ecommerce_data.domains.retail.sewing_rows import (
    DEPARTMENT,
    OWNERS,
    PURLWICK,
    YARN,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _row(code: str, weight: str, material: str, brand: str, description: str, price: float):
    attrs = (a("yarn_weight", "Yarn weight", weight), a("material", "Material", material))
    params = (("yarn_weight", weight.lower()), ("material", material.lower()))
    return row(code, f"{weight} {material} Yarn", brand, YARN, "Yarn", "yarn", description, attrs,
               packs((1, price), (5, round(price * 4.6, 2)), (10, round(price * 8.8, 2))), params)  # fmt: skip


ROWS = (
    _row(
        "YRNDKM",
        "DK",
        "Merino Wool",
        PURLWICK,
        "A soft, springy double knit yarn in a 50 g ball, for sweaters, hats and baby clothes on 4 mm needles.",
        6.5,
    ),
    _row(
        "YRNARC",
        "Aran",
        "Cotton",
        LANTERNBY,
        "A smooth, cool yarn in a 100 g ball with crisp stitch definition, for summer tops, dishcloths and bags.",
        5.0,
    ),
    _row(
        "YRNCHA",
        "Chunky",
        "Acrylic",
        THISTLE,
        "A thick, quick-knitting yarn in a 100 g ball that machine washes, for blankets, scarves and cushions.",
        4.0,
    ),
    _row(
        "YRN4PA",
        "4 Ply",
        "Alpaca",
        PURLWICK,
        "A fine, warm yarn with a soft halo in a 50 g ball, for socks, shawls and lace on 3 mm needles.",
        8.5,
    ),
)

SPEC = TypeSpec(
    key="yarn",
    department=DEPARTMENT,
    product_type="Yarn",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "green yarn", "vocabulary", decoy(ROWS[1], "YRNGBD", "Aran Cotton Yarn with a Green Ball Band",
              "A blue cotton yarn in a ball band printed with the knitting pattern.", BLUE)),
        Decoy(6, "black yarn", "generic", decoy(ROWS[0], "YRNBSH", "Black Sheep DK Merino Wool Yarn",
              "From the Black Sheep range: an undyed white double knit yarn.", WHITE)),
    ),
)  # fmt: skip
