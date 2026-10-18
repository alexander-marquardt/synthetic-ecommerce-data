"""Nursery storage (gen#213): a fabric basket, a cube bin with a drawer and a hanging organizer,
drawn by :func:`kit_baby.nursery_storage` with the kind they state."""

from __future__ import annotations

from babywear_rows import (
    BLACK,
    BLUE,
    CREAM,
    DOVECOTE,
    FENWOLD,
    GREEN,
    GREY,
    HUSHWELL,
    NAVY,
    PINK,
    RED,
    SAGE,
    THISTLE,
    WHITE,
    YELLOW,
    a,
    decoy,
    nursery,
)
from type_registry import TypeSpec

_L = "Nursery Storage"
_KIND = {"Basket": "basket", "Cube": "cube", "Hanging Organizer": "hanging"}


def _s(code, title, brand, price, desc, colors, kind, fabric):  # fmt: skip
    return nursery(
        code, title, brand, _L, "Nursery Storage", "nursery_storage", price, desc, colors,
        (a("storage_type", "Storage type", kind), a("fabric", "Fabric", fabric)),
        (("kind", _KIND[kind]),),
    )  # fmt: skip


_ROWS = (
    _s("NYSBSK", "Fabric Nursery Storage Basket", FENWOLD, 12.0,
       "A soft sided basket with handle cut-outs, for toys, nappies and blankets.",
       (BLUE, GREY, WHITE, YELLOW), "Basket", "Cotton"),
    _s("NYSCUB", "Nursery Storage Cube with Drawer", HUSHWELL, 18.0,
       "A fabric cube bin with a pull-out drawer, for a shelf unit or a cot-side shelf.",
       (GREEN, PINK, BLACK), "Cube", "Felt"),
    _s("NYSHNG", "Hanging Nursery Storage Organizer", THISTLE, 15.0,
       "A hanging organizer with four deep pockets, for the back of a door or a wardrobe rail.",
       (RED, CREAM, SAGE), "Hanging Organizer", "Polyester"),
    _s("NYSBSL", "Large Nursery Storage Basket", DOVECOTE, 16.0,
       "A large fabric basket for the nursery floor, with two handles.",
       (NAVY, WHITE, YELLOW), "Basket", "Cotton"),
)  # fmt: skip

SPEC = TypeSpec(
    key="nursery_storage",
    department="Home",
    product_type="Nursery Storage",
    rows=_ROWS,
    decoys=(
        decoy(1, "pink nursery storage", _ROWS[1], 13, "Pink Drawer Nursery Storage Cube",
              "A green cube bin with a pink drawer front; the bin is green.", color=GREEN),
        decoy(4, "wooden nursery storage", _ROWS[0], 14, "Wooden Look Nursery Storage Basket",
              "A fabric basket printed with a wood grain; there is no wood in it.", color=GREY),
        decoy(2, "nursery shelf", _ROWS[3], 15, "Nursery Shelf Basket",
              "A fabric basket that sits on a shelf; it is a basket and the shelf is not included.",
              color=NAVY),
        decoy(7, "thistle", _ROWS[2], 16, "Thistle & Wren Hanging Nursery Organizer",
              "A hanging organizer from Thistle & Wren; the name is the maker's, with no thistle.",
              color=RED),
    ),
)  # fmt: skip
