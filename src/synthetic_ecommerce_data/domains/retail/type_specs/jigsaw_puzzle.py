"""Jigsaw Puzzle (Toys), registered by its spec (gen#537); a breadth type since gen#960.

**Toys > Puzzles > Jigsaw Puzzles.** The older styles stay in ``toys_rows`` as templates only
(the ``homes`` entry). The rows here are ``derivable``: each title shows the picture's theme and
the piece count ("Seaside 500 Piece Jigsaw Puzzle"), and the scaled build draws more jigsaws by
the theme, one of the five pictures :func:`kit_toys.jigsaw` draws. The piece count has a unit, so
a derived style keeps it, with the age range and the finished size that follow it
(``scale_text.FROZEN_KEYS``) and the grid of exactly that many tiles. One SKU per style.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_toys,  # noqa: F401 -- registers jigsaw
)
from synthetic_ecommerce_data.domains.retail.toys_play_common import (
    BLUE,
    FERNBY,
    GREEN,
    MATERIAL_CLAIM,
    ORANGE,
    PIPWICK,
    PUDDLE,
    RED,
    YELLOW,
    age,
    count,
    measured,
    style,
    toy_decoy,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Home, Row, TypeSpec, a

_PATH = ("Toys", "Puzzles", "Jigsaw Puzzles")
CALDERBY, LANTERNBY, THISTLE = "Calderby & Lune", "Lanternby", "Thistle & Wren"


def _jigsaw(code: str, theme: str, n: int, brand: str, years: int, size: tuple[int, int], color,
            price: float) -> Row:  # fmt: skip
    """A jigsaw of ``n`` pieces showing ``theme``: its finished size is a text and its length
    and width in centimeters; 1000 pieces and more are for adults."""
    length, width = size
    desc = (f"A {theme.lower()} picture cut into {n} interlocking pieces, with a poster of the "
            f"finished picture in the box. It measures {length} x {width} cm made up. For ages "
            f"{years} and up.")  # fmt: skip
    return style(
        code,
        f"{theme} {n} Piece Jigsaw Puzzle",
        brand,
        _PATH,
        "Jigsaw Puzzle",
        "jigsaw",
        desc,
        (color,),
        (
            count("piece_count", "Piece count", n),
            a("theme", "Theme", theme),
            age(f"{years}+ years"),
            a("finished_size", "Finished size", f"{length} x {width} cm"),
            measured("item_length", "Item length", length, "CMT"),
            measured("item_width", "Item width", width, "CMT"),
        ),
        price,
        audience="adult" if n >= 1000 else "kids",
        params=(("pieces", str(n)), ("theme", theme.lower())),
        colorless=True,
    )


ROWS = (
    _jigsaw("JGBSEA", "Seaside", 100, PIPWICK, 6, (49, 36), BLUE, 10.0),
    _jigsaw("JGBDIN", "Dinosaur", 200, FERNBY, 7, (49, 36), GREEN, 11.0),
    _jigsaw("JGBMAP", "World Map", 300, PUDDLE, 8, (49, 36), YELLOW, 12.0),
    _jigsaw("JGBSPA", "Space", 500, CALDERBY, 10, (49, 36), BLUE, 14.0),
    _jigsaw("JGBLAN", "Landscape", 750, LANTERNBY, 12, (59, 42), GREEN, 15.0),
    _jigsaw("JGBSEK", "Seaside", 1000, THISTLE, 12, (68, 49), ORANGE, 17.0),
    _jigsaw("JGBMAK", "World Map", 1500, FERNBY, 14, (85, 60), RED, 20.0),
    _jigsaw("JGBSPK", "Space", 2000, PIPWICK, 14, (98, 68), BLUE, 24.0),
    _jigsaw("JGBLAS", "Landscape", 150, PUDDLE, 6, (40, 30), GREEN, 10.0),
    _jigsaw("JGBDIM", "Dinosaur", 400, CALDERBY, 9, (49, 36), ORANGE, 13.0),
    _jigsaw("JGBSEM", "Seaside", 600, LANTERNBY, 10, (59, 42), BLUE, 15.0),
    _jigsaw("JGBLAK", "Landscape", 1200, THISTLE, 12, (68, 49), GREEN, 18.0),
)  # fmt: skip

SPEC = TypeSpec(
    key="jigsaw_puzzle",
    department="Toys",
    product_type="Jigsaw Puzzle",
    rows=ROWS,
    derivable=True,
    decoys=(
        toy_decoy(6, "card game", "generic", ROWS[2], 42, "Card Game Club Jigsaw Puzzle",
                  "From the Card Game Club range, named after a village hall; it is a 300 piece "
                  "jigsaw puzzle of a world map, and there are no cards in the box.", color=GREEN),
        toy_decoy(4, "wooden jigsaw puzzle", MATERIAL_CLAIM, ROWS[3], 43,
                  "Wooden-Look Jigsaw Puzzle",
                  "A 500 piece jigsaw on board printed with a wood grain; the pieces are card, "
                  "not wood.", color=ORANGE),
    ),
    homes=(Home("toys_rows", False),),
)  # fmt: skip
