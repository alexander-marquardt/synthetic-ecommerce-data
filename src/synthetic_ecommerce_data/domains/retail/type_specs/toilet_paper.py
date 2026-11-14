"""Toilet Paper (gen#962): Cleaning > Paper Goods > Toilet Paper.

A breadth type: ``derivable`` True, so the scaled build draws more rolls from these four by the
values their titles show (the finish, the ply and the roll size). The paper is white and sold
without a color; each SKU is a pack of 4 to 24 rolls. :func:`kit_paper.toilet_roll` draws the
roll's size, its plies and a quilted or recycled finish.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.paper_rows import (
    DEPARTMENT,
    FEATHERLEE,
    HOLLINSBY,
    MOSSDOWN,
    OWNERS,
    TOILET,
    decoy,
    packs,
    roll,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec


def _packs(base: float) -> tuple[tuple[str, float], ...]:
    """Packs of 4, 6, 9, 12, 18 and 24 rolls, priced up from ``base``."""
    return packs(*((n, round(base * f, 2)) for n, f in
                   ((4, 1.0), (6, 1.45), (9, 2.1), (12, 2.7), (18, 3.9), (24, 5.0))))  # fmt: skip


def _params(finish: str, ply: str, roll_size: str) -> tuple[tuple[str, str], ...]:
    return (("finish", finish.lower()), ("ply", ply.lower()), ("roll_size", roll_size.lower()))


ROWS = (
    row("TPSOFT", "Ultra Soft 2-Ply Toilet Paper, Double Rolls", FEATHERLEE, TOILET, "Toilet Paper", "toilet_roll",
        "Ultra Soft toilet paper with a cushioned 2-Ply sheet that tears cleanly at each perforation. Double Rolls last twice as long as a standard roll.",
        roll("Ultra Soft", "2-Ply", "Double"), _packs(3.5), _params("Ultra Soft", "2-Ply", "Double")),
    row("TPQUIL", "Quilted 3-Ply Toilet Paper, Mega Rolls", MOSSDOWN, TOILET, "Toilet Paper", "toilet_roll",
        "Quilted toilet paper with a thick 3-Ply sheet. Mega Rolls hold more sheets, so the roll is changed less often.",
        roll("Quilted", "3-Ply", "Mega"), _packs(4.5), _params("Quilted", "3-Ply", "Mega")),
    row("TPSTRG", "Ultra Strong 4-Ply Toilet Paper, Regular Rolls", HOLLINSBY, TOILET, "Toilet Paper", "toilet_roll",
        "Ultra Strong toilet paper: a 4-Ply sheet that holds together when wet. Regular Rolls fit every holder.",
        roll("Ultra Strong", "4-Ply", "Regular"), _packs(4.0), _params("Ultra Strong", "4-Ply", "Regular")),
    row("TPRECY", "Recycled 2-Ply Toilet Paper, Regular Rolls", MOSSDOWN, TOILET, "Toilet Paper", "toilet_roll",
        "Recycled toilet paper made from recovered office paper, with a 2-Ply sheet and a plastic-free paper wrap.",
        roll("Recycled", "2-Ply", "Regular"), _packs(3.0), _params("Recycled", "2-Ply", "Regular")),
)

SPEC = TypeSpec(
    key="toilet_paper",
    department=DEPARTMENT,
    product_type="Toilet Paper",
    derivable=True,
    rows=ROWS,
    owners=OWNERS,
    decoys=(
        Decoy(4, "quilted toilet paper", "vocabulary", decoy(ROWS[0], "TPSMTH", "Smooth 2-Ply Toilet Paper, Double Rolls",
              "A smooth Ultra Soft sheet with no quilted pattern, for those who prefer a flat finish.")),
        Decoy(6, "quilted toilet paper", "generic", decoy(ROWS[2], "TPQHIL", "Quilted Hill Ultra Strong 4-Ply Toilet Paper, Regular Rolls",
              "From the Quilted Hill range: an Ultra Strong 4-Ply sheet with a flat finish.")),
    ),
)  # fmt: skip
