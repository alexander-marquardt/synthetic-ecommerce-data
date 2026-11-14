"""Facial Tissues (gen#962): Cleaning > Paper Goods > Facial Tissues.

A breadth type: ``derivable`` True, so the scaled build draws more boxes from these four by the
values their titles show (the finish, the ply and the box). The tissues are white; the box is the
SKU's color, in the six main colors (gen#275). Each SKU is a color in a pack of 1, 4, 8 or 12
boxes. :func:`kit_paper.tissue_box` draws a cube or a flat box and the tissue's plies.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.paper_rows import (
    CLEARBROOK,
    DEPARTMENT,
    FEATHERLEE,
    HOLLINSBY,
    MOSSDOWN,
    OWNERS,
    SIX,
    TISSUES,
    WHITE,
    YELLOW,
    decoy,
    packs,
    row,
    tissue,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec


def _packs(base: float) -> tuple[tuple[str, float], ...]:
    """Packs of 1, 4, 8 and 12 boxes, priced up from ``base``."""
    return packs(*((n, round(base * f, 2)) for n, f in ((1, 1.0), (4, 3.6), (8, 6.8), (12, 9.6))))


def _params(ply: str, box: str) -> tuple[tuple[str, str], ...]:
    return (("ply", ply.lower()), ("box", box.lower()))


ROWS = (
    row("FTLOTN", "Lotion 3-Ply Facial Tissues, Cube Box", FEATHERLEE, TISSUES, "Facial Tissues", "tissue_box",
        "Lotion facial tissues: a soft 3-Ply tissue for a sore nose, in a Cube Box that stands on a desk or a bedside table.",
        tissue("Lotion", "3-Ply", "Cube"), _packs(2.0), _params("3-Ply", "Cube"), SIX),
    row("FTALOE", "Aloe Vera 2-Ply Facial Tissues, Flat Box", MOSSDOWN, TISSUES, "Facial Tissues", "tissue_box",
        "Aloe Vera facial tissues with a gentle 2-Ply tissue, in a Flat Box that slides into a drawer or a car door.",
        tissue("Aloe Vera", "2-Ply", "Flat"), _packs(1.8), _params("2-Ply", "Flat"), SIX),
    row("FTXSFT", "Extra Soft 2-Ply Facial Tissues, Cube Box", HOLLINSBY, TISSUES, "Facial Tissues", "tissue_box",
        "Extra Soft facial tissues for every day: a 2-Ply tissue that pulls up one at a time from a Cube Box.",
        tissue("Extra Soft", "2-Ply", "Cube"), _packs(1.5), _params("2-Ply", "Cube"), SIX),
    row("FTMENT", "Menthol 3-Ply Facial Tissues, Flat Box", CLEARBROOK, TISSUES, "Facial Tissues", "tissue_box",
        "Menthol facial tissues with a cooling scent that helps a blocked nose: a 3-Ply tissue in a Flat Box.",
        tissue("Menthol", "3-Ply", "Flat"), _packs(2.2), _params("3-Ply", "Flat"), SIX),
)

SPEC = TypeSpec(
    key="facial_tissues",
    department=DEPARTMENT,
    product_type="Facial Tissues",
    derivable=True,
    rows=ROWS,
    owners=OWNERS,
    decoys=(
        Decoy(4, "red tissues", "vocabulary", decoy(ROWS[2], "FTRDTR", "Red Trim Extra Soft 2-Ply Facial Tissues, Cube Box",
              "Extra Soft facial tissues in a white box with a red trim around the opening.", (WHITE,))),
        Decoy(6, "blue tissues", "generic", decoy(ROWS[1], "FTBLBY", "Blue Bay Aloe Vera 2-Ply Facial Tissues, Flat Box",
              "From the Blue Bay range: Aloe Vera facial tissues in a yellow box.", (YELLOW,))),
    ),
)  # fmt: skip
