"""Marble run (gen#424): wooden and plastic marble runs, sold by piece count.

**Toys > Building & Construction > Marble Runs**: five styles from three invented brands, drawn by
:func:`kit_toys_play.marble_run`. The material and the age range are structured entries; the
SKUs are the piece count (``piece_count``, a counted entry on every SKU) on one shared box
drawing that prints no count. A marble run has no color selector. Not derivable.
"""

from __future__ import annotations

import kit_toys_play  # noqa: F401 -- registers marble_run
from toys_play_common import (
    BLUE,
    EIGHT,
    FERNBY,
    GREEN,
    MATERIAL_CLAIM,
    PINK,
    PIPWICK,
    PUDDLE,
    YELLOW,
    age,
    kind,
    sizes,
    style,
    toy_decoy,
)
from type_registry import Row, TypeSpec, a

_PATH = ("Toys", "Building & Construction", "Marble Runs")


def _run(code: str, title: str, brand: str, material: str, tiers: int, years: str, desc: str,
         pieces: tuple[tuple[int, float], ...]) -> Row:  # fmt: skip
    return style(
        code,
        title,
        brand,
        _PATH,
        "Marble Run",
        "marble_run",
        desc,
        EIGHT[:1],
        (kind("Marble Run"), a("material", "Material", material), age(years)),
        pieces[0][1],
        sizes(*pieces),
        "piece_count",
        params=(("tiers", str(tiers)),),
        colorless=True,
    )


_ROWS = (
    _run("MRNWD1", "Wooden Marble Run Tower", FERNBY, "Wood", 4, "4+ years",
         "Stack the beech tracks, ramps and funnels into a tower and send the marbles down. "
         "Sold as a 50, 100 or 150 piece set. For ages 4 and up.",
         ((50, 20.0), (100, 35.0), (150, 50.0))),
    _run("MRNWD2", "Wooden Marble Run Starter Set", PUDDLE, "Wood", 3, "3+ years",
         "A first marble run of chunky wooden tracks that click together. Sold as a 30 or "
         "60 piece set. For ages 3 and up.", ((30, 15.0), (60, 25.0))),
    _run("MRNPL1", "Plastic Marble Run Adventure", PIPWICK, "Plastic", 4, "5+ years",
         "Snap clear tubes, spirals and tracks into a run that rattles, spins and drops. "
         "Sold as a 60, 100 or 150 piece set. For ages 5 and up.",
         ((60, 18.0), (100, 28.0), (150, 40.0))),
    _run("MRNPL2", "Glow in the Dark Marble Run", PIPWICK, "Plastic", 3, "6+ years",
         "A marble run whose tracks glow after a minute in the light, with glowing marbles. "
         "Sold as an 80 or 120 piece set. For ages 6 and up.", ((80, 24.0), (120, 34.0))),
    _run("MRNWD3", "Wooden Marble Run Coaster", FERNBY, "Wood", 4, "5+ years",
         "A wooden coaster with a lift, a loop and a long finishing track. Sold as a 40, 80 "
         "or 120 piece set. For ages 5 and up.", ((40, 18.0), (80, 32.0), (120, 46.0))),
)  # fmt: skip
_BRAND = "Play Kitchen Co"

SPEC = TypeSpec(
    key="marble_run",
    department="Toys",
    product_type="Marble Run",
    rows=_ROWS,
    decoys=(
        toy_decoy(6, "card game", "generic", _ROWS[0], 24, "Card Game Row Marble Run",
                  "From the Card Game Row range, named after a terrace of cottages; it is a "
                  "marble run, not a game of cards.", color=GREEN),
        toy_decoy(6, "dolls house", "generic", _ROWS[1], 25, "Dolls House Lane Marble Run",
                  "From the Dolls House Lane range, named after a row of cottages; it is a "
                  "marble run.", color=PINK),
        toy_decoy(4, "wooden marble run", MATERIAL_CLAIM, _ROWS[2], 26, "Wooden-Look Marble Run",
                  "A plastic marble run printed with a wood grain; there is no wood in it.",
                  color=YELLOW),
        toy_decoy(7, "play kitchen", "generic", _ROWS[3], 27, "Play Kitchen Co Marble Run",
                  "A marble run from Play Kitchen Co; the name is the maker's, not a "
                  "kitchen.", brand=_BRAND, color=BLUE),
    ),
    owners=((_BRAND, "own"),),
)  # fmt: skip
