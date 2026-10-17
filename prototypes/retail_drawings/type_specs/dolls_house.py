"""Dolls' house (gen#424): wooden and plastic houses, sold in four styles.

**Toys > Dolls & Accessories > Dolls' Houses**: four styles from three invented brands, drawn
by :func:`kit_toys_play.dolls_house`. The rooms, the floors, whether furniture is included
and the material are structured entries; the SKUs are the house's style (``style``). A house
has no color selector: its finishes are the style. Not derivable: authored rows only.
"""

from __future__ import annotations

import kit_toys_play  # noqa: F401 -- registers dolls_house
from toys_play_common import (
    BLUE,
    EIGHT,
    FERNBY,
    GREEN,
    MATERIAL_CLAIM,
    PIPWICK,
    PUDDLE,
    RED,
    YELLOW,
    age,
    count,
    kind,
    sizes,
    style,
    toy_decoy,
    yes,
)
from type_registry import Row, TypeSpec, a

_PATH = ("Toys", "Dolls & Accessories", "Dolls' Houses")
_STYLES = ("Classic", "Pastel", "Natural", "Bright")


def _house(code: str, title: str, brand: str, material: str, rooms: int, floors: int,
           furniture: bool, years: str, desc: str, price: float) -> Row:  # fmt: skip
    return style(
        code,
        title,
        brand,
        _PATH,
        "Dolls' House",
        "dolls_house",
        desc,
        EIGHT[:1],
        (
            kind("Dolls' House"),
            count("rooms", "Rooms", rooms),
            count("floors", "Floors", floors),
            a("furniture_included", "Furniture included", yes(furniture)),
            a("material", "Material", material),
            age(years),
        ),
        price,
        sizes(*((s, price) for s in _STYLES)),
        "house_style",
        params=(("floors", str(floors)),),
        colorless=True,
    )


_ROWS = (
    _house("DHSWD2", "Wooden Dolls House with Furniture", FERNBY, "Wood", 4, 2, True,
           "3+ years", "A two floor wooden dolls house with four rooms, a staircase, a "
           "front door that opens and 20 pieces of furniture. For ages 3 and up.", 85.0),
    _house("DHSWD3", "Three Storey Wooden Dolls House", PUDDLE, "Wood", 6, 3, False,
           "4+ years", "A tall wooden house with six rooms on three floors and a balcony. "
           "Add your furniture later. For ages 4 and up.", 120.0),
    _house("DHSPL2", "Plastic Dolls House with Furniture", PIPWICK, "Plastic", 4, 2, True,
           "3+ years", "A two floor plastic house that folds flat, with four rooms and a "
           "set of furniture. For ages 3 and up.", 45.0),
    _house("DHSPL3", "Plastic Mansion Dolls House", PIPWICK, "Plastic", 6, 3, True,
           "4+ years", "A three floor plastic mansion with six rooms, a lift and furniture "
           "for every room. For ages 4 and up.", 75.0),
)  # fmt: skip
_BRAND = "Kite Lane Toys"

SPEC = TypeSpec(
    key="dolls_house",
    department="Toys",
    product_type="Dolls' House",
    rows=_ROWS,
    decoys=(
        toy_decoy(6, "yellow dolls house", "generic", _ROWS[0], 16, "Yellow Ridge Dolls House",
                  "From the Yellow Ridge range, named after a hill; the house itself is "
                  "painted blue.", color=BLUE),
        toy_decoy(6, "kite", "generic", _ROWS[1], 17, "Kite Hill Dolls House",
                  "From the Kite Hill range, named after a windy field; a house for dolls "
                  "that does not fly.", color=GREEN),
        toy_decoy(4, "wooden dolls house", MATERIAL_CLAIM, _ROWS[2], 18, "Wooden-Look Dolls House",
                  "A plastic house moulded and printed to look like wood; there is no wood in "
                  "it.", color=RED),
        toy_decoy(7, "kite", "generic", _ROWS[3], 19, "Kite Lane Toys Dolls House",
                  "A three floor mansion from Kite Lane Toys; the name is the maker's, not a "
                  "toy that flies.", brand=_BRAND, color=YELLOW),
    ),
    owners=((_BRAND, "own"),),
)  # fmt: skip
