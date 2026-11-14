"""Paper Towels (gen#962): Cleaning > Paper Goods > Paper Towels.

A breadth type: ``derivable`` True, so the scaled build draws more rolls from these four by the
values their titles show (the finish, the sheet and the roll size). The paper is white and sold
without a color; each SKU is a pack of 2 to 12 rolls. :func:`kit_paper.paper_towel_roll` draws the
roll's size, its perforations (closer for a half sheet) and an embossed or recycled finish.
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
    TOWELS,
    decoy,
    packs,
    row,
    towel,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec


def _packs(base: float) -> tuple[tuple[str, float], ...]:
    """Packs of 2, 4, 6, 8 and 12 rolls, priced up from ``base``."""
    return packs(*((n, round(base * f, 2)) for n, f in
                   ((2, 1.0), (4, 1.9), (6, 2.7), (8, 3.5), (12, 5.0))))  # fmt: skip


def _params(finish: str, sheet: str, roll_size: str) -> tuple[tuple[str, str], ...]:
    return (("finish", finish.lower()), ("sheet", sheet.lower()), ("roll_size", roll_size.lower()))


ROWS = (
    row("PTABSB", "Extra Absorbent Paper Towels, Full Sheet, Double Rolls", MOSSDOWN, TOWELS, "Paper Towels", "paper_towel_roll",
        "Extra Absorbent paper towels that soak up spills in one wipe. Each Full Sheet tears off at its perforation, and Double Rolls last twice as long.",
        towel("Extra Absorbent", "Full Sheet", "Double"), _packs(3.0), _params("Extra Absorbent", "Full Sheet", "Double")),
    row("PTSTRG", "Ultra Strong Paper Towels, Half Sheet, Triple Rolls", HOLLINSBY, TOWELS, "Paper Towels", "paper_towel_roll",
        "Ultra Strong paper towels that scrub a worktop without tearing. A Half Sheet takes only what a small spill needs, and Triple Rolls go a long way.",
        towel("Ultra Strong", "Half Sheet", "Triple"), _packs(4.5), _params("Ultra Strong", "Half Sheet", "Triple")),
    row("PTEMBS", "Embossed Paper Towels, Half Sheet, Regular Rolls", FEATHERLEE, TOWELS, "Paper Towels", "paper_towel_roll",
        "Embossed paper towels with a raised pattern that traps crumbs and grease. A Half Sheet for small jobs, on Regular Rolls that fit any holder.",
        towel("Embossed", "Half Sheet", "Regular"), _packs(2.5), _params("Embossed", "Half Sheet", "Regular")),
    row("PTRECY", "Recycled Paper Towels, Full Sheet, Regular Rolls", CLEARBROOK, TOWELS, "Paper Towels", "paper_towel_roll",
        "Recycled paper towels made from recovered paper, on Regular Rolls in a plastic-free paper wrap.",
        towel("Recycled", "Full Sheet", "Regular"), _packs(2.2), _params("Recycled", "Full Sheet", "Regular")),
)

SPEC = TypeSpec(
    key="paper_towels",
    department=DEPARTMENT,
    product_type="Paper Towels",
    derivable=True,
    rows=ROWS,
    owners=OWNERS,
    decoys=(
        Decoy(4, "embossed paper towels", "vocabulary", decoy(ROWS[0], "PTSMTH", "Smooth Paper Towels, Full Sheet, Double Rolls",
              "Extra Absorbent paper towels with a flat sheet that is not embossed, for wiping glass and screens.")),
        Decoy(6, "embossed paper towels", "generic", decoy(ROWS[3], "PTEROW", "Embossed Row Recycled Paper Towels, Full Sheet, Regular Rolls",
              "From the Embossed Row range: recycled paper towels with a flat sheet.")),
    ),
)  # fmt: skip
