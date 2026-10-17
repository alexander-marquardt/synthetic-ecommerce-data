"""Kite (gen#424): diamond, delta, parafoil and stunt kites in the six main colors.

**Toys > Outdoor Toys > Kites**: five styles from three invented brands, drawn by
:func:`kit_toys_play.kite`. A kite's span is a structured entry in centimetres, its kind is
the shape (and the ``toy_type`` facet value) and its age range is the toy rule of gen#201. The
SKUs are the colors (the six main ones and two more). Not derivable: authored rows only.
"""

from __future__ import annotations

import kit_toys_play  # noqa: F401 -- registers kite
from toys_play_common import (
    BLUE,
    EIGHT,
    FERNBY,
    GREEN,
    MATERIAL_CLAIM,
    PIPWICK,
    PUDDLE,
    WHITE,
    YELLOW,
    age,
    kind,
    measured,
    style,
    toy_decoy,
)
from type_registry import Row, TypeSpec

_PATH = ("Toys", "Outdoor Toys", "Kites")


def _kite(code: str, title: str, brand: str, shape_kind: str, span: float, years: str,
          desc: str, price: float) -> Row:  # fmt: skip
    return style(
        code,
        title,
        brand,
        _PATH,
        "Kite",
        "kite",
        desc,
        EIGHT,
        (kind(f"{shape_kind.title()} Kite"), measured("span", "Span", span, "CMT"), age(years)),
        price,
        params=(("kind", shape_kind),),
    )


_ROWS = (
    _kite("KITDIA", "Diamond Kite with Tail", PIPWICK, "diamond", 70, "5+ years",
          "A classic diamond kite with a ribbon tail, a fibreglass frame and 30 m of line "
          "on a winder. Flies in a light breeze. For ages 5 and up.", 7.0),
    _kite("KITDLT", "Delta Kite for Beginners", FERNBY, "delta", 110, "6+ years",
          "A delta kite that lifts in a gentle wind and is easy to launch. Comes with 40 m "
          "of line. For ages 6 and up.", 10.0),
    _kite("KITPAR", "Parafoil Kite, Frameless", PUDDLE, "parafoil", 160, "8+ years",
          "A frameless parafoil kite of ripstop nylon that packs small and pulls hard in a "
          "steady wind, on 50 m of line. For ages 8 and up.", 18.0),
    _kite("KITSTN", "Stunt Kite, Dual Line", PIPWICK, "stunt", 120, "10+ years",
          "A dual line stunt kite that loops, dives and hovers, with two handles and 30 m "
          "lines. Fast in a good wind. For ages 10 and up.", 22.0),
    _kite("KITSTP", "Pocket Stunt Kite", FERNBY, "stunt", 90, "8+ years",
          "A small stunt kite on two short lines for beginners, with a pair of foam handles "
          "and a carry bag. For ages 8 and up.", 14.0),
)  # fmt: skip
_BRAND = "Marble Run Co"

SPEC = TypeSpec(
    key="kite",
    department="Toys",
    product_type="Kite",
    rows=_ROWS,
    decoys=(
        toy_decoy(6, "red kite", "generic", _ROWS[0], 8, "Red Tarn Kite",
                  "From the Red Tarn range, named after a hill walk; the kite itself is blue.",
                  color=BLUE),
        toy_decoy(6, "card game", "generic", _ROWS[1], 9, "Card Game Ridge Kite",
                  "From the Card Game Ridge range, named after a hill path; it is a delta kite, "
                  "not a game of cards.", color=GREEN),
        toy_decoy(4, "silk kite", MATERIAL_CLAIM, _ROWS[0], 10, "Silk-Look Kite",
                  "A diamond kite of ripstop nylon printed to look like silk; there is no silk "
                  "in it.", color=YELLOW),
        toy_decoy(7, "marble run", "generic", _ROWS[3], 11, "Marble Run Co Stunt Kite",
                  "A dual line stunt kite from Marble Run Co; the name is the maker's, not a "
                  "toy.", brand=_BRAND, color=WHITE),
    ),
    owners=((_BRAND, "own"),),
)  # fmt: skip
