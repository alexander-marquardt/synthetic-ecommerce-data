"""Play kitchen (gen#424): wooden and plastic kitchens with an oven door, a sink or sounds.

**Toys > Pretend Play > Play Kitchens**: four styles from three invented brands, drawn by
:func:`kit_toys_play.play_kitchen`. The material, the height in centimetres and three
features (lights and sounds, a sink, an oven door) are structured entries; the SKUs are the
colors (the six main ones and two more). The Role Play Toys leaf keeps its two older kitchens.
"""

from __future__ import annotations

import kit_toys_play  # noqa: F401 -- registers play_kitchen
from toys_play_common import EIGHT, FERNBY, PIPWICK, PUDDLE, age, kind, measured, style, yes
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


SPEC = TypeSpec(
    key="play_kitchen",
    department="Toys",
    product_type="Play Kitchen",
    rows=(
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
    ),
)  # fmt: skip
