"""Sideboards (gen#1022 slice 5): Home > Furniture > Sideboards.

The first of the home types drawn for the issue's new shapes to ship in the retail build with
products of its own. Each row is the generator's own: its brand from the brand book, its title,
description, price, colors and size are written here, and nothing comes from a benchmark.

What changes a sideboard's picture is its style, not a SKU: the doors, the drawers and the base
are drawing params of the ``sideboard`` shape (:mod:`kit_storage_furniture`), and each is a
structured attribute beside it (``door_count``, ``drawer_count``, ``base_style``). The size is
stated once per style (``item_width``, ``item_height``, ``item_depth``), so a style's SKUs differ
only in color. The rows are templates only (``derivable`` False), so the seeded derivation is
what it was. ``tests/test_sideboard_ships_1022.py`` holds them to the build's product-split and
non-copying audits.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_storage_furniture,  # noqa: F401 -- registers the sideboard shape
)
from synthetic_ecommerce_data.domains.retail.type_registry import BRAND_OWNER, Row, TypeSpec, cw

#: The brands these rows sell, each a furniture brand with a house style.
BRANDS = ("Brackenmere Home", "Larchwood Living", "Emberly Home", "Cobble & Kiln")
PATH = ("Home", "Furniture", "Sideboards")
#: Each base the ``sideboard`` shape draws, as its attribute value.
BASES = {"tapered": "Tapered legs", "plinth": "Plinth", "hairpin": "Hairpin legs"}

NATURAL = cw("Natural", "#c9a06a", accent="#7a5a3a")
DARK_BROWN = cw("Dark Brown", "#5e3b25")
WHITE, GREY, BLACK = cw("White", "#f2efe8"), cw("Grey", "#9a9ca0"), cw("Black", "#2b2b2e")
GREEN, NAVY = cw("Green", "#3f6b4f"), cw("Navy", "#26324a")


def _count(key: str, name: str, n: int) -> tuple[str, str, str, str]:
    """A count (unit code C62): a facet ranges over it."""
    return (key, name, str(n), "C62")


def _cm(key: str, name: str, v: int) -> tuple[str, str, str, str, float]:
    return (key, name, str(v), "CMT", float(v * 10))  # canonical length is millimeters


#: (code, title, brand, doors, drawers, base, material, colors, (width, height, depth) cm, price, description)
_SIDEBOARDS = (
    ("SDBOK3", "Oak Sideboard with 3 Doors and 3 Drawers", BRANDS[0], 3, 3, "tapered", "Oak", (NATURAL, WHITE, BLACK), (160, 80, 45), 549.0,
     "A long oak sideboard on tapered legs, with three drawers for cutlery and table linen over three cupboards for plates and serving dishes."),
    ("SDBWN2", "Walnut Sideboard with 2 Doors", BRANDS[1], 2, 0, "hairpin", "Walnut", (DARK_BROWN, GREY), (120, 75, 40), 429.0,
     "A low walnut sideboard on slim metal hairpin legs, its two doors opening on one adjustable shelf, for a dining room or under a television."),
    ("SDBPN4", "Painted Pine Sideboard with 4 Doors", BRANDS[2], 4, 0, "plinth", "Pine", (WHITE, GREEN, NAVY), (180, 85, 45), 599.0,
     "A wide painted pine sideboard standing on a plinth, with four panelled doors and two shelves behind each pair, for a farmhouse kitchen or dining room."),
    ("SDBMG4", "Mango Wood Sideboard with 4 Drawers", BRANDS[3], 0, 4, "tapered", "Mango Wood", (NATURAL, BLACK), (100, 85, 40), 389.0,
     "A compact mango wood sideboard of four deep drawers on tapered legs, for a hallway or the end of a dining room."),
    ("SDBAS1", "Ash Sideboard with 1 Door and 2 Drawers", BRANDS[0], 1, 2, "plinth", "Ash", (NATURAL, GREY), (110, 80, 42), 459.0,
     "A small ash sideboard on a plinth, two drawers beside one cupboard, sized for a narrow dining room wall."),
)  # fmt: skip


def _row(code, title, brand, doors, drawers, base, mat, colors, size, price, text) -> Row:
    width, height, depth = size
    return Row(
        code, title, brand, "Home", PATH, "Sideboard", price, "sideboard", text, colors,
        (_count("door_count", "Door count", doors), _count("drawer_count", "Drawer count", drawers),
         ("base_style", "Base style", BASES[base]), ("material", "Material", mat),
         _cm("item_width", "Item width", width), _cm("item_height", "Item height", height),
         _cm("item_depth", "Item depth", depth), ("room", "Room", "Dining Room")),
        params=(("doors", str(doors)), ("drawers", str(drawers)), ("legs", base)),
    )  # fmt: skip


SPEC = TypeSpec(
    key="sideboard",
    department="Home",
    product_type="Sideboard",
    # Brackenmere Home is the shop's own label; the other three are sold, not owned.
    owners=tuple((b, BRAND_OWNER.get(b, "third_party")) for b in BRANDS),
    rows=tuple(_row(*s) for s in _SIDEBOARDS),
)
