"""Mutation rows for the underwear drawn values (gen#245), kept out of ``mutation_check.py``.

Each row plants one defect that makes two values of a drawn attribute draw the same, or a
length or a denier draw out of order, and names the tests that must go red.
``mutation_check.py`` turns them into ``Mutation`` rows named ``underwear drawn values: ...``
(``--only "underwear drawn values:"`` re-runs them). A row is
``(name, file, old, new, test, property)``; the root is ``prototypes/retail_drawings``.
"""

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_underwear_drawn_values_245.py"
_SAME = f"{_T}::test_each_value_of_a_drawn_attribute_draws_differently"

ROWS: list[tuple[str, str, str, str, str | tuple[str, ...], str]] = [
    (
        "a thong is drawn as a brief",
        "underwear_rows.py",
        '"High-Leg": "high_leg", "Thong": "thong",',
        '"High-Leg": "high_leg", "Thong": "brief",',
        f"{_SAME}[Knickers-cut]",
        "each knicker cut draws its own outline",
    ),
    (
        "a high-leg is drawn as a bikini",
        "underwear_rows.py",
        '"High-Leg": "high_leg", "Thong"',
        '"High-Leg": "bikini", "Thong"',
        f"{_SAME}[Knickers-cut]",
        "each knicker cut draws its own outline",
    ),
    (
        "every slip hangs at the midi hem",
        "kit_underwear.py",
        'SLIP_HEM = {"mini": 284, "midi": 322, "full": 358}',
        'SLIP_HEM = {"mini": 322, "midi": 322, "full": 322}',
        f"{_T}::test_a_longer_garment_hangs_lower[Slip]",
        "a longer slip hangs lower",
    ),
    (
        "every dressing gown hangs at the knee",
        "kit_underwear.py",
        'GOWN_HEM = {"short": 262, "knee": 308, "full": 356}',
        'GOWN_HEM = {"short": 308, "knee": 308, "full": 308}',
        f"'{_T}::test_a_longer_garment_hangs_lower[Dressing Gown]'",
        "a longer gown hangs lower",
    ),
    (
        "every tights denier is drawn at one opacity",
        "kit_underwear.py",
        'DENIER_OPACITY = {"10": 0.42, "15": 0.5, "20": 0.6, "40": 0.78, "60": 0.9, "100": 1.0}',
        'DENIER_OPACITY = {"10": 0.6, "15": 0.6, "20": 0.6, "40": 0.6, "60": 0.6, "100": 0.6}',
        (f"{_SAME}[Tights-denier]", f"{_T}::test_a_higher_denier_is_drawn_more_opaque"),
        "each denier draws its own opacity",
    ),
    (
        "two deniers share an opacity",
        "kit_underwear.py",
        '"10": 0.42, "15": 0.5,',
        '"10": 0.5, "15": 0.5,',
        f"{_SAME}[Tights-denier]",
        "each denier draws its own opacity",
    ),
    (
        "a heavier denier is drawn fainter",
        "kit_underwear.py",
        '"40": 0.78, "60": 0.9, "100": 1.0}',
        '"40": 0.78, "60": 0.7, "100": 0.6}',
        f"{_T}::test_a_higher_denier_is_drawn_more_opaque",
        "a higher denier is drawn more opaque",
    ),
    (
        "a crop vest is drawn as a strappy one",
        "underwear_rows.py",
        '"Crop": "crop", "Sleeveless"',
        '"Crop": "strappy", "Sleeveless"',
        f"{_SAME}[Vest-style]",
        "each vest style draws its own outline",
    ),
    (
        "a bra-friendly bodysuit is drawn as a plain one",
        "underwear_rows.py",
        '"Bra-Friendly Bodysuit": "bra_friendly",',
        '"Bra-Friendly Bodysuit": "bodysuit",',
        f"{_SAME}[Shapewear-shapewear_type]",
        "each shapewear type draws its own outline",
    ),
    (
        "boxer shorts are drawn as trunks",
        "underwear_rows.py",
        '"Boxer Shorts": "boxer", "Briefs": "brief"}',
        '"Boxer Shorts": "trunks", "Briefs": "brief"}',
        f"{_SAME}[Boxers-fit]",
        "each boxer fit draws its own outline",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "underwear drawn values"


def rows() -> list[Row]:
    return [Row(*r, "prototypes/retail_drawings") for r in ROWS]
