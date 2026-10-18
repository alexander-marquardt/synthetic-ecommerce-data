"""Nappy caddies (gen#213): open carry totes with a handle and a pocket for each compartment,
drawn by :func:`kit_baby.nappy_caddy` with the pocket count they state."""

from __future__ import annotations

from babywear_rows import (
    BLACK,
    BLUE,
    CREAM,
    FENWOLD,
    GREEN,
    GREY,
    HUSHWELL,
    NAVY,
    PINK,
    QUILLON,
    RED,
    SAGE,
    THISTLE,
    WHITE,
    YELLOW,
    a,
    count,
    decoy,
    nursery,
    yes,
)
from type_registry import TypeSpec

_L = "Nappy Caddies"


def _c(code, title, brand, price, desc, colors, pockets, wipe, size):  # fmt: skip
    return nursery(
        code, title, brand, _L, "Nappy Caddy", "nappy_caddy", price, desc, colors,
        (count("compartments", "Compartments", pockets), a("wipe_clean", "Wipe-clean", yes(wipe)),
         a("caddy_size", "Caddy size", size)),
        (("compartments", str(pockets)),),
    )  # fmt: skip


_ROWS = (
    _c("NYCTHR", "Three Compartment Nappy Caddy", FENWOLD, 14.0,
       "A fabric caddy with three pockets for nappies, wipes and balm, and a carry handle.",
       (BLUE, GREY, WHITE, YELLOW), 3, False, "Standard"),
    _c("NYCTWO", "Wipe-Clean Nappy Caddy", HUSHWELL, 12.0,
       "A wipe-clean caddy with two big sections, for the changing table.",
       (GREEN, PINK, BLACK), 2, True, "Small"),
    _c("NYCFOR", "Large Four Pocket Nappy Caddy", QUILLON, 18.0,
       "A large caddy with four pockets, to keep the changing station tidy.",
       (RED, CREAM, SAGE), 4, False, "Large"),
    _c("NYCSTR", "Canvas Nappy Caddy with Dividers", THISTLE, 16.0,
       "A canvas caddy with three sections and a sturdy handle.",
       (NAVY, WHITE, YELLOW), 3, False, "Standard"),
)  # fmt: skip

SPEC = TypeSpec(
    key="nappy_caddy",
    department="Home",
    product_type="Nappy Caddy",
    rows=_ROWS,
    decoys=(
        decoy(1, "black nappy caddy", _ROWS[0], 9, "Black Handle Nappy Caddy",
              "A grey caddy with a black carry handle; the caddy itself is grey.", color=GREY),
        decoy(4, "waterproof nappy caddy", _ROWS[2], 10, "Waterproof Nappy Caddy",
              "A cotton caddy that is not waterproof: spot clean only.", color=RED),
        decoy(2, "nappy bag", _ROWS[3], 11, "Nappy Bag Style Canvas Caddy",
              "A caddy that stays at home: it has no shoulder strap and is not a changing bag.",
              color=NAVY),
        decoy(6, "bunny", _ROWS[1], 12, "Bunny Lane Nappy Caddy",
              "From the Bunny Lane range, named after a road; there is no rabbit on it.",
              color=GREEN),
    ),
)  # fmt: skip
