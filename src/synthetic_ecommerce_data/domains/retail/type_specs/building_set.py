"""Building Set (Toys), registered by its spec (gen#537); a breadth type since gen#960 (slice 2).

**Toys > Building & Construction > Building Sets.** The older sets stay in the shared row modules
named by ``homes``, as templates only, and the Barry Plotter range (gen#925), which the spec
reads from :mod:`barry_plotter`, is never derived (:func:`scale.left_out`). The rows here are
``derivable``: each title shows the theme and the model the set builds ("Pirate Tower Building
Set"), so the scaled build draws more sets by those two values, and the drawing follows them
(:func:`kit_toys_figures.brick_box`: the theme on the box, the model in its corner). A building
set's SKUs are its piece counts; it has no color selector (the exception its rows declare
under ruling 2026-10-13, gen#275). Every row is for ages 6 and up, so a derived style keeps
its age.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    barry_plotter,
    kit_toys_figures,  # noqa: F401 -- registers brick_box
)
from synthetic_ecommerce_data.domains.retail.toys_play_common import (
    BLUE,
    FERNBY,
    GREEN,
    MATERIAL_CLAIM,
    ORANGE,
    PUDDLE,
    RED,
    YELLOW,
    age,
    kind,
    sizes,
    style,
    toy_decoy,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Home, Row, TypeSpec, a

_PATH = ("Toys", "Building & Construction", "Building Sets")
CALDERBY, LANTERNBY, THISTLE = "Calderby & Lune", "Lanternby", "Thistle & Wren"

#: The opening sentences: each names the theme and nothing that holds for one model only.
_LEADS = (
    "Build the {t} scene brick by brick.",
    "The {t} box art shows the finished model on its baseplate.",
    "Everything for a whole {t} adventure, in bricks.",
    "Start the {t} collection that grows with every set.",
)


def _set(code: str, theme: str, model: str, brand: str, lead: str, color, price: float) -> Row:
    """A building set: "<theme> <model> Building Set", sold in four piece counts."""
    toy_type = f"{model} Building Set"
    desc = (f"{lead.format(t=theme)} This {toy_type.lower()} fits every standard brick and "
            f"comes in four box sizes. For ages 6 and up.")  # fmt: skip
    return style(
        code,
        f"{theme} {toy_type}",
        brand,
        _PATH,
        "Building Set",
        "brick_box",
        desc,
        (color,),
        (a("theme", "Theme", theme), kind(toy_type), age("6+ years")),
        price,
        sizes(("120", price), ("320", round(price * 2.2)), ("750", round(price * 4.5)),
              ("1500", round(price * 8.0))),
        "piece_count",
        params=(("kind", toy_type.lower()), ("theme", theme.lower())),
        colorless=True,
    )


ROWS = (
    _set("BLDSPV", "Space", "Vehicle", CALDERBY, _LEADS[0], BLUE, 12.0),
    _set("BLDCAT", "Castle", "Tower", LANTERNBY, _LEADS[1], RED, 14.0),
    _set("BLDCYV", "City", "Vehicle", THISTLE, _LEADS[2], YELLOW, 11.0),
    _set("BLDDIC", "Dinosaurs", "Creature", FERNBY, _LEADS[3], GREEN, 13.0),
    _set("BLDFMT", "Farm", "Tower", PUDDLE, _LEADS[0], ORANGE, 10.0),
    _set("BLDPIR", "Pirate", "Vehicle", CALDERBY, _LEADS[1], BLUE, 15.0),
    _set("BLDJUN", "Jungle", "Creature", LANTERNBY, _LEADS[2], GREEN, 12.0),
    _set("BLDOCE", "Ocean", "Creature", THISTLE, _LEADS[3], BLUE, 13.0),
    _set("BLDARC", "Arctic", "Vehicle", FERNBY, _LEADS[0], BLUE, 11.0),
    _set("BLDDES", "Desert", "Tower", PUDDLE, _LEADS[1], YELLOW, 12.0),
    _set("BLDFOR", "Fairy Forest", "Tower", CALDERBY, _LEADS[2], GREEN, 14.0),
    _set("BLDROB", "Robot", "Creature", LANTERNBY, _LEADS[3], RED, 16.0),
    _set("BLDRAC", "Racing", "Vehicle", THISTLE, _LEADS[0], RED, 13.0),
    _set("BLDMAG", "Magma", "Tower", FERNBY, _LEADS[1], ORANGE, 15.0),
    _set("BLDHAR", "Harbour", "Vehicle", PUDDLE, _LEADS[2], BLUE, 12.0),
    _set("BLDLUN", "Lunar", "Tower", CALDERBY, _LEADS[3], YELLOW, 17.0),
)  # fmt: skip

SPEC = TypeSpec(
    key="building_set",
    department="Toys",
    product_type="Building Set",
    rows=(*barry_plotter.rows_of("Building Set"), *ROWS),
    derivable=True,
    homes=(
        Home("decoy_product_words", False),
        Home("toys_rows", False),
    ),
    decoys=(
        toy_decoy(6, "water gun", "generic", ROWS[5], 54, "Water Gun Bay Pirate Building Set",
                  "From the Water Gun Bay range, named after a smugglers' bay; it is a building "
                  "set, and nothing in the box squirts."),
        toy_decoy(4, "wooden building set", MATERIAL_CLAIM, ROWS[1], 55,
                  "Wooden-Look Castle Building Set",
                  "A building set whose bricks are printed with a wood grain; they are plastic."),
    ),
)  # fmt: skip
