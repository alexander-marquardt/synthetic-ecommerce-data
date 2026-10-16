"""Play kitchen (gen#424): wooden and plastic kitchens with an oven door, a sink or sounds.

**Toys > Pretend Play > Play Kitchens**: four styles from three invented brands, drawn by
:func:`kit_toys_play.play_kitchen`. The material, the height in centimetres and three
features (lights and sounds, a sink, an oven door) are structured entries; the SKUs are the
colors (the six main ones and two more). The Role Play Toys leaf keeps its two older kitchens.
"""

from __future__ import annotations

import kit_toys_play  # noqa: F401 -- registers play_kitchen
from toys_play_common import (
    EIGHT,
    FERNBY,
    GREEN,
    MATERIAL_CLAIM,
    PINK,
    PIPWICK,
    PUDDLE,
    RED,
    WHITE,
    age,
    kind,
    measured,
    style,
    toy_decoy,
    yes,
)
from type_registry import Row, TypeSpec, a

_PATH = ("Toys", "Pretend Play", "Play Kitchens")


def _kit(code: str, title: str, brand: str, material: str, cm: float, sounds: bool, sink: bool,
         oven: bool, years: str, desc: str, price: float) -> Row:  # fmt: skip
    return style(
        code,
        title,
        brand,
        _PATH,
        "Play Kitchen",
        "play_kitchen",
        desc,
        EIGHT,
        (
            kind("Play Kitchen"),
            a("material", "Material", material),
            measured("height_cm", "Height", cm, "CMT"),
            a("lights_and_sounds", "Lights and sounds", yes(sounds)),
            a("has_sink", "Sink", yes(sink)),
            a("oven_door", "Oven door", yes(oven)),
            age(years),
        ),
        price,
        params=(("sink", "yes" if sink else "no"),),
    )


_ROWS = (
    _kit("PKTWSO", "Wooden Play Kitchen with Sink and Oven", FERNBY, "Wood", 95, False, True,
         True, "3+ years", "A solid wood toy kitchen with a hob, an oven door that opens, a "
         "sink with a tap that turns and a shelf for pans. For ages 3 and up.", 95.0),
    _kit("PKTWCR", "Wooden Corner Play Kitchen", PUDDLE, "Wood", 85, False, False, True,
         "3+ years", "A wooden kitchen that fits a corner, with an oven door and a hob "
         "that clicks. For ages 3 and up.", 70.0),
    _kit("PKTPLS", "Plastic Play Kitchen with Lights and Sounds", PIPWICK, "Plastic", 80,
         True, True, True, "2+ years", "A wipe-clean kitchen with a sizzling hob, a talking "
         "oven and a tap that gurgles. For ages 2 and up.", 55.0),
    _kit("PKTPLC", "Compact Plastic Play Kitchen", PIPWICK, "Plastic", 60, True, False, False,
         "2+ years", "A small kitchen for a toddler, with a hob that lights up and a "
         "microwave. For ages 2 and up.", 35.0),
)  # fmt: skip
_BRAND = "Card Game Row"

SPEC = TypeSpec(
    key="play_kitchen",
    department="Toys",
    product_type="Play Kitchen",
    rows=_ROWS,
    decoys=(
        toy_decoy(6, "green play kitchen", "generic", _ROWS[0], 12, "Green Hollow Play Kitchen",
                  "From the Green Hollow range, named after a wooded dip; the kitchen itself is "
                  "red.", color=RED),
        toy_decoy(6, "water gun", "generic", _ROWS[1], 13, "Water Gun Bay Play Kitchen",
                  "From the Water Gun Bay range, named after a beach; it is a corner kitchen "
                  "and squirts no water.", color=PINK),
        toy_decoy(4, "wooden play kitchen", MATERIAL_CLAIM, _ROWS[2], 14,
                  "Wooden-Look Play Kitchen",
                  "A plastic kitchen with a printed wood grain finish; there is no wood in it.",
                  color=WHITE),
        toy_decoy(7, "card game", "generic", _ROWS[3], 15, "Card Game Row Play Kitchen",
                  "A compact kitchen from Card Game Row; the name is the maker's, not a game.",
                  brand=_BRAND, color=GREEN),
    ),
    owners=((_BRAND, "own"),),
)  # fmt: skip
