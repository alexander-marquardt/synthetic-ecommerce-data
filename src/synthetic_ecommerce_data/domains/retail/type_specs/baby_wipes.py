"""Baby Wipes (gen#965, slice 1): Kids > Baby > Diapering > Baby Wipes.

A breadth type: ``derivable`` True, so the scaled build draws more wipes from these four by the
values their titles show (the scent and the wipe). A pack carries no color; its one pack color is
drawn (:func:`kit_baby_gear.wipes_pack`) with its lid, a flip top or a resealable flap. Each SKU is
a pack size: a single pack, or 3, 6 or 12 packs.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.baby_gear_rows import (
    CALDERBY,
    DEPARTMENT,
    FENWOLD,
    LEMON,
    LILAC,
    LITTLE_FERNBY,
    MINT,
    MIREFIELD,
    PEACH,
    QUILLON,
    SKY,
    THISTLE,
    WIPES,
    decoy,
    packs,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a


def _wipes(scent: str, kind: str, lid: str) -> tuple[tuple, ...]:
    return (a("scent", "Scent", scent), a("wipe_type", "Wipe type", kind),
            a("lid", "Lid", lid))  # fmt: skip


def _drawn(lid: str) -> tuple[tuple[str, str], ...]:
    return (("lid", lid.lower()),)


ROWS = (
    row("BWPUSN", "Unscented Sensitive Baby Wipes", LITTLE_FERNBY, WIPES, "Baby Wipes", "wipes_pack",
        "Soft, fragrance-free wipes for newborn skin, for changes and sticky hands.",
        _wipes("Unscented", "Sensitive", "Flip Top"), packs((1, 1.5), (3, 4.0), (6, 7.5), (12, 14.0)), "pack_size", _drawn("Flip Top"), (SKY,), colorless=True),
    row("BWPATC", "Aloe Vera Thick Cleansing Baby Wipes", MIREFIELD, WIPES, "Baby Wipes", "wipes_pack",
        "Extra thick wipes with a touch of aloe vera that lift away mess in one sweep.",
        _wipes("Aloe Vera", "Thick Cleansing", "Resealable"), packs((1, 2.0), (3, 5.5), (6, 10.0), (12, 18.0)), "pack_size", _drawn("Resealable"), (MINT,), colorless=True),
    row("BWPCBD", "Chamomile Biodegradable Baby Wipes", THISTLE, WIPES, "Baby Wipes", "wipes_pack",
        "Plant-fiber wipes that break down in home compost, lightly scented with chamomile.",
        _wipes("Chamomile", "Biodegradable", "Resealable"), packs((1, 2.5), (3, 7.0), (6, 13.0), (12, 24.0)), "pack_size", _drawn("Resealable"), (PEACH,), colorless=True),
    row("BWPCPW", "Cucumber Pure Water Baby Wipes", FENWOLD, WIPES, "Baby Wipes", "wipes_pack",
        "Wipes made almost entirely of purified water, with a fresh hint of cucumber.",
        _wipes("Cucumber", "Pure Water", "Flip Top"), packs((1, 2.0), (3, 5.5), (6, 10.5), (12, 19.0)), "pack_size", _drawn("Flip Top"), (LILAC,), colorless=True),
    row("BWPCES", "Coconut Extra Soft Baby Wipes", QUILLON, WIPES, "Baby Wipes", "wipes_pack",
        "Cloth-soft wipes with a light coconut scent, for faces, hands and changes.",
        _wipes("Coconut", "Extra Soft", "Flip Top"), packs((1, 1.8), (3, 5.0), (6, 9.5), (12, 17.0)), "pack_size", _drawn("Flip Top"), (LEMON,), colorless=True),
    row("BWPCLT", "Calendula Thick Cleansing Baby Wipes", CALDERBY, WIPES, "Baby Wipes", "wipes_pack",
        "Thick wipes with soothing calendula that clean up the messiest changes in one sweep.",
        _wipes("Calendula", "Thick Cleansing", "Resealable"), packs((1, 2.2), (3, 6.0), (6, 11.0), (12, 20.0)), "pack_size", _drawn("Resealable"), (SKY,), colorless=True),
)  # fmt: skip

SPEC = TypeSpec(
    key="baby_wipes",
    department=DEPARTMENT,
    product_type="Baby Wipes",
    derivable=True,
    rows=ROWS,
    decoys=(
        Decoy(2, "wipes dispenser", "category", decoy(ROWS[0], "BWPDSP", "Wipes Dispenser Refill: Unscented Sensitive Baby Wipes",
              "A refill pack of unscented wipes to top up a wipes dispenser: the wipes only, no dispenser.")),
        Decoy(6, "lavender baby wipes", "generic", decoy(ROWS[3], "BWPLVL", "Lavender Lane Cucumber Pure Water Baby Wipes",
              "From the Lavender Lane range: pure water wipes with a fresh cucumber scent.")),
    ),
)  # fmt: skip
