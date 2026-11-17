"""Doll (Toys), registered by its spec (gen#537); a breadth type since gen#960 (slice 2).

**Toys > Dolls & Accessories > Dolls.** The older dolls stay in the shared row modules named by
``homes``, as templates only. The rows here are ``derivable``: each title shows the outfit's
theme and the kind of doll ("Mermaid Rag Doll"), so the scaled build draws more dolls by those
two values, and the drawing follows them (:func:`kit_toys_figures.doll_box`: the doll of the
kind in a window box, the theme on its panel). Every row is sold in the six main colors of
the outfit (ruling 2026-10-13, gen#275) and is for ages 3 and up, so a derived style keeps its
age.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_toys_figures,  # noqa: F401 -- registers doll_box
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
from synthetic_ecommerce_data.domains.retail.type_registry import Home, Row, TypeSpec, a

_PATH = ("Toys", "Dolls & Accessories", "Dolls")
CALDERBY, LANTERNBY, THISTLE = "Calderby & Lune", "Lanternby", "Thistle & Wren"
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)

#: The opening sentences: each names the outfit's theme and nothing that holds for one kind only.
_LEADS = (
    "The {t} outfit comes with a matching hat and shoes.",
    "Every piece of the {t} outfit is made to dress and undress.",
    "Her {t} look comes with a little bag to carry.",
    "Play out a whole {t} day, then swap the outfit for pyjamas.",
)


def _doll(code: str, theme: str, sort: str, brand: str, lead: str, price: float) -> Row:
    """A doll: "<theme> <sort> Doll", in the six main colors of the outfit."""
    toy_type = f"{sort} Doll"
    desc = (f"{lead.format(t=theme)} This {toy_type.lower()} comes with a spare outfit. "
            f"For ages 3 and up.")  # fmt: skip
    return style(
        code,
        f"{theme} {toy_type}",
        brand,
        _PATH,
        "Doll",
        "doll_box",
        desc,
        SIX,
        (a("theme", "Theme", theme), kind(toy_type), age("3+ years")),
        price,
        params=(("kind", toy_type.lower()), ("theme", theme.lower())),
    )


ROWS = (
    _doll("DOLBAL", "Ballerina", "Fashion", LANTERNBY, _LEADS[0], 16.0),
    _doll("DOLAST", "Astronaut", "Rag", THISTLE, _LEADS[1], 14.0),
    _doll("DOLMER", "Mermaid", "Baby", CALDERBY, _LEADS[2], 18.0),
    _doll("DOLFAI", "Fairy", "Fashion", FERNBY, _LEADS[3], 15.0),
    _doll("DOLPOP", "Pop Star", "Fashion", PUDDLE, _LEADS[0], 17.0),
    _doll("DOLEXP", "Explorer", "Rag", LANTERNBY, _LEADS[1], 13.0),
    _doll("DOLGAR", "Gardener", "Baby", THISTLE, _LEADS[2], 19.0),
    _doll("DOLART", "Artist", "Rag", CALDERBY, _LEADS[3], 12.0),
    _doll("DOLSKA", "Skater", "Fashion", FERNBY, _LEADS[0], 16.0),
    _doll("DOLPIL", "Pilot", "Baby", PUDDLE, _LEADS[1], 20.0),
    _doll("DOLBEA", "Beach Day", "Fashion", CALDERBY, _LEADS[2], 14.0),
    _doll("DOLSNO", "Snow Day", "Rag", LANTERNBY, _LEADS[3], 15.0),
    _doll("DOLUNI", "Unicorn", "Fashion", THISTLE, _LEADS[0], 17.0),
    _doll("DOLCAM", "Camping", "Rag", FERNBY, _LEADS[1], 13.0),
    _doll("DOLTEN", "Tennis", "Fashion", PUDDLE, _LEADS[2], 15.0),
    _doll("DOLBIR", "Birthday Party", "Baby", CALDERBY, _LEADS[3], 18.0),
)  # fmt: skip

SPEC = TypeSpec(
    key="doll",
    department="Toys",
    product_type="Doll",
    rows=ROWS,
    derivable=True,
    homes=(
        Home("decoy_rows", False),
        Home("decoy_product_words", False),
        Home("toys_rows", False),
    ),
    decoys=(
        toy_decoy(6, "night light", "generic", ROWS[0], 52, "Night Light Ballerina Fashion Doll",
                  "From the Night Light range, named after her bedtime story; it is a doll and "
                  "gives no light.", color=WHITE),
        toy_decoy(4, "porcelain doll", MATERIAL_CLAIM, ROWS[3], 53, "Porcelain-Look Fashion Doll",
                  "A fashion doll with a face painted to look like porcelain; the doll is vinyl.",
                  color=RED),
    ),
)  # fmt: skip
