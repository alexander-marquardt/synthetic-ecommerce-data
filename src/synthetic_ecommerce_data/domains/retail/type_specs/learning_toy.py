"""Learning Toy (Toys), a breadth type of gen#960 (slice 3).

**Toys > Learning Toys > Early Learning.** Each title shows the toy's theme and its kind
("Farmyard Friends Shape Sorter"), so the scaled build draws more learning toys by those two
values, and the drawing follows them (:func:`kit_toys_learning.learning_toy`: an activity cube,
a shape sorter, a learning tablet or a counting abacus, the theme on the panel). Every template
is sold in the six main colors (ruling 2026-10-13, gen#275) and is for ages 18 months and up,
so a derived style keeps its age. Every theme is invented (ruling 2026-10-30, gen#720).
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_toys_learning,  # noqa: F401 -- registers learning_toy
)
from synthetic_ecommerce_data.domains.retail.toys_play_common import (
    BLACK,
    BLUE,
    FERNBY,
    GREEN,
    MATERIAL_CLAIM,
    PUDDLE,
    RED,
    WHITE,
    YELLOW,
    age,
    kind,
    style,
    toy_decoy,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Row, TypeSpec, a

_PATH = ("Toys", "Learning Toys", "Early Learning")
CALDERBY, LANTERNBY, THISTLE = "Calderby & Lune", "Lanternby", "Thistle & Wren"
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)

#: The opening sentences: each names the theme and nothing that holds for one toy only.
_LEADS = (
    "The {t} pictures teach first words, colors and shapes.",
    "Little hands learn to match and sort with the {t} friends.",
    "Every {t} piece is chunky, smooth and easy to hold.",
    "Play and learn with the {t} characters, one step at a time.",
)


def _toy(code: str, theme: str, toy: str, brand: str, lead: str, price: float) -> Row:
    """A learning toy: "<theme> <toy>", in the six main colors."""
    desc = (f"{lead.format(t=theme)} This {toy.lower()} is a learning toy that wipes clean. "
            f"For ages 18 months and up.")  # fmt: skip
    return style(
        code,
        f"{theme} {toy}",
        brand,
        _PATH,
        "Learning Toy",
        "learning_toy",
        desc,
        SIX,
        (a("theme", "Theme", theme), kind(toy), age("18+ months")),
        price,
        params=(("kind", toy.lower()), ("theme", theme.lower())),
    )


ROWS = (
    _toy("LRNFAR", "Farmyard Friends", "Shape Sorter", CALDERBY, _LEADS[0], 16.0),
    _toy("LRNJUN", "Jungle Pals", "Activity Cube", LANTERNBY, _LEADS[1], 24.0),
    _toy("LRNOWL", "Clever Owl", "Learning Tablet", THISTLE, _LEADS[2], 19.0),
    _toy("LRNBEE", "Busy Bee", "Counting Abacus", FERNBY, _LEADS[3], 14.0),
    _toy("LRNSEA", "Sea Buddies", "Shape Sorter", PUDDLE, _LEADS[0], 15.0),
    _toy("LRNTRN", "Choo Choo Station", "Activity Cube", CALDERBY, _LEADS[1], 27.0),
    _toy("LRNPUP", "Puppy Pals", "Learning Tablet", LANTERNBY, _LEADS[2], 18.0),
    _toy("LRNLAD", "Garden Beetle", "Counting Abacus", THISTLE, _LEADS[3], 13.0),
    _toy("LRNDIN", "Dino Discovery", "Shape Sorter", FERNBY, _LEADS[0], 17.0),
    _toy("LRNSPA", "Little Astronaut", "Activity Cube", PUDDLE, _LEADS[1], 26.0),
    _toy("LRNPEN", "Penguin Parade", "Learning Tablet", CALDERBY, _LEADS[2], 20.0),
    _toy("LRNMON", "Cheeky Monkey", "Counting Abacus", LANTERNBY, _LEADS[3], 15.0),
    _toy("LRNPOL", "Polar Pals", "Shape Sorter", THISTLE, _LEADS[0], 16.0),
    _toy("LRNCIR", "Big Top Circus", "Activity Cube", FERNBY, _LEADS[1], 28.0),
    _toy("LRNBUN", "Bunny Hop", "Learning Tablet", PUDDLE, _LEADS[2], 17.0),
    _toy("LRNCAT", "Snail Trail", "Counting Abacus", CALDERBY, _LEADS[3], 12.0),
    _toy("LRNBAR", "Barnyard Band", "Activity Cube", LANTERNBY, _LEADS[0], 25.0),
    _toy("LRNTUR", "Turtle Cove", "Shape Sorter", THISTLE, _LEADS[1], 14.0),
    _toy("LRNROB", "Robot Workshop", "Learning Tablet", FERNBY, _LEADS[2], 22.0),
    _toy("LRNPAN", "Panda Forest", "Counting Abacus", PUDDLE, _LEADS[3], 13.0),
)  # fmt: skip

SPEC = TypeSpec(
    key="learning_toy",
    department="Toys",
    product_type="Learning Toy",
    rows=ROWS,
    derivable=True,
    decoys=(
        toy_decoy(
            6,
            "kite",
            "generic",
            ROWS[2],
            64,
            "Kite Club Learning Tablet",
            "Its pictures show a kite club at the park; it is a learning tablet, not a kite.",
            color=BLUE,
        ),
        toy_decoy(
            4,
            "wooden shape sorter",
            MATERIAL_CLAIM,
            ROWS[0],
            65,
            "Wooden-Look Shape Sorter",
            "A shape sorter printed with a wood grain; the box and the shapes are plastic.",
            color=RED,
        ),
    ),
)
