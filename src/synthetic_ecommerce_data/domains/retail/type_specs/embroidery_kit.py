"""Embroidery Kit (gen#1118, cut 3): Office & School > Sewing & Knitting > Embroidery Kits.

A breadth type: ``derivable`` True, so the scaled build draws more kits from these four by the
values their titles show (the motif and the kind of embroidery). The SKU is the floss color the
motif is worked in, a kit sold singly. The drawing shows the wooden hoop, the motif on its linen
as a grid of crosses or a satin stitched shape, and two skeins of the floss
(:func:`kit_sewing_notions.embroidery_kit`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_sewing_notions,  # noqa: F401 -- registers embroidery_kit
)
from synthetic_ecommerce_data.domains.retail.office_rows import (
    BLUE,
    CALDERBY,
    GREEN,
    decoy,
    packs,
)
from synthetic_ecommerce_data.domains.retail.sewing_rows import (
    DEPARTMENT,
    EMBROIDERY,
    OWNERS,
    PURLWICK,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _row(code: str, motif: str, kit_type: str, brand: str, description: str, price: float):
    attrs = (a("motif", "Motif", motif), a("kit_type", "Kit type", kit_type))
    params = (("kit_type", kit_type.lower()), ("motif", motif.lower()))
    return row(code, f"{motif} {kit_type} Embroidery Kit", brand, EMBROIDERY, "Embroidery Kit", "embroidery_kit",
               description, attrs, packs((1, price)), params)  # fmt: skip


ROWS = (
    _row(
        "EMKFCS",
        "Floral",
        "Cross Stitch",
        PURLWICK,
        "A beginner's kit with a printed chart, counted cotton fabric, a wooden hoop, a needle and the floss to stitch a flower.",
        16.0,
    ),
    _row(
        "EMKHCS",
        "Heart",
        "Cross Stitch",
        PURLWICK,
        "A small kit with a printed chart, counted cotton fabric, a wooden hoop, a needle and the floss to stitch a heart.",
        12.0,
    ),
    _row(
        "EMKFST",
        "Floral",
        "Stamped",
        CALDERBY,
        "A kit whose linen comes printed with a flower to fill in satin stitch, with a wooden hoop, two needles and the floss.",
        22.0,
    ),
    _row(
        "EMKHST",
        "Heart",
        "Stamped",
        CALDERBY,
        "A kit whose linen comes printed with a heart to fill in satin stitch, with a wooden hoop, a needle and the floss.",
        18.0,
    ),
)

SPEC = TypeSpec(
    key="embroidery_kit",
    department=DEPARTMENT,
    product_type="Embroidery Kit",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "black embroidery kit", "vocabulary", decoy(ROWS[0], "EMKBHP", "Floral Cross Stitch Embroidery Kit with a Black Hoop",
              "A flower worked in green floss, in a hoop with a dark stained rim.", GREEN)),
        Decoy(6, "red embroidery kit", "generic", decoy(ROWS[2], "EMKRRB", "Red Robin Floral Stamped Embroidery Kit",
              "From the Red Robin range: a stamped flower to fill in blue floss.", BLUE)),
    ),
)  # fmt: skip
