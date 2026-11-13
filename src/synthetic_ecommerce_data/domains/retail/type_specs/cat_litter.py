"""Cat Litter (gen#967, slice 1): a bag of litter, sold by its net weight.

**Pets > Litter & Hygiene > Cat Litter** holds bags whose title names the scent and the litter
type (clumping clay, silica crystal, wood pellet, recycled paper, clumping corn); each SKU is a
bag's net weight. :mod:`kit_pets` draws the bag with its own granules in the window.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.pets_rows import (
    CLUMPTON,
    DEPARTMENT,
    FOREST,
    LITTER,
    NAVY,
    OWNERS,
    PINEHOLLOW,
    PLUM,
    SAND,
    SKY,
    TEAL,
    WHISKERBY,
    decoy,
    grams,
    row,
)  # fmt: skip
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _litter(scent: str, kind: str) -> tuple[tuple, ...]:
    return (a("animal", "Animal", "Cat"), a("scent", "Scent", scent),
            a("litter_type", "Litter type", kind))  # fmt: skip


def _drawn(kind: str) -> tuple[tuple[str, str], ...]:
    return (("litter_type", kind.lower()),)


ROWS = (
    row("CTLUCC", "Unscented Clumping Clay Cat Litter", CLUMPTON, LITTER, "Cat Litter", "cat_litter",
        "A fine clay litter that forms firm clumps for easy scooping and locks away odors.",
        _litter("Unscented", "Clumping Clay"), grams((5, 4.0), (10, 7.5), (15, 10.0), (20, 13.0)), "net_weight_g", _drawn("Clumping Clay"), SKY),
    row("CTLLSC", "Lavender Silica Crystal Cat Litter", WHISKERBY, LITTER, "Cat Litter", "cat_litter",
        "Light crystals that soak up moisture and odors and last up to a month.",
        _litter("Lavender", "Silica Crystal"), grams((2, 6.0), (3.8, 10.0), (7.6, 18.0)), "net_weight_g", _drawn("Silica Crystal"), PLUM),
    row("CTLPWP", "Pine Wood Pellet Cat Litter", PINEHOLLOW, LITTER, "Cat Litter", "cat_litter",
        "Natural pellets from reclaimed softwood that break down to sawdust as they absorb.",
        _litter("Pine", "Wood Pellet"), grams((5, 4.5), (10, 8.0), (15, 11.0), (30, 19.0)), "net_weight_g", _drawn("Wood Pellet"), FOREST),
    row("CTLURP", "Unscented Recycled Paper Cat Litter", PINEHOLLOW, LITTER, "Cat Litter", "cat_litter",
        "Soft pellets of recycled paper, gentle on paws after surgery and on kittens.",
        _litter("Unscented", "Recycled Paper"), grams((5, 5.0), (10, 9.0), (15, 12.5)), "net_weight_g", _drawn("Recycled Paper"), SAND),
    row("CTLFCC", "Fresh Linen Clumping Corn Cat Litter", CLUMPTON, LITTER, "Cat Litter", "cat_litter",
        "A plant-based litter of ground corn that clumps and can go in the compost.",
        _litter("Fresh Linen", "Clumping Corn"), grams((3, 6.0), (6, 11.0), (10, 16.0)), "net_weight_g", _drawn("Clumping Corn"), TEAL),
    row("CTLBNC", "Baby Powder Non-Clumping Clay Cat Litter", WHISKERBY, LITTER, "Cat Litter", "cat_litter",
        "A coarse clay litter that absorbs at the bottom of the tray, for a full change each week.",
        _litter("Baby Powder", "Non-Clumping Clay"), grams((5, 3.5), (10, 6.5), (20, 11.5)), "net_weight_g", _drawn("Non-Clumping Clay"), NAVY),
)  # fmt: skip

SPEC = TypeSpec(
    key="cat_litter",
    department=DEPARTMENT,
    product_type="Cat Litter",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(2, "litter tray", "category", decoy(ROWS[0], "CTLTRY", "Litter Tray Refill: Unscented Clumping Clay Cat Litter",
              "A bag of clumping clay litter to refill a litter tray: the litter only, no tray.")),
        Decoy(6, "lavender cat litter", "generic", decoy(ROWS[2], "CTLLAV", "Lavender Hill Pine Wood Pellet Cat Litter",
              "From the Lavender Hill range: natural pine pellets with no added scent.")),
    ),
)  # fmt: skip
