"""Changing mats (gen#213): wipe-clean and quilted mats with raised edges and side pockets,
drawn by :func:`kit_baby.changing_mat` with the surface and the pocket count they state."""

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
    count,
    decoy,
    nursery,
    yes,
)
from type_registry import TypeSpec

_L = "Changing Mats"


def _m(code, title, brand, price, desc, colors, wipe, pockets, size):  # fmt: skip
    return nursery(
        code, title, brand, _L, "Changing Mat", "changing_mat", price, desc, colors,
        (a("wipe_clean", "Wipe-clean", yes(wipe)), count("compartments", "Compartments", pockets),
         a("mat_size", "Mat size", size)),
        (("wipe_clean", "yes" if wipe else "no"), ("compartments", str(pockets))),
    )  # fmt: skip


_ROWS = (
    _m("NYMWPC", "Wipe-Clean Changing Mat with Pockets", FENWOLD, 16.0,
       "A padded wipe-clean mat with raised edges and two side pockets for wipes and balm.",
       (BLUE, PINK, WHITE, YELLOW), True, 2, "Standard"),
    _m("NYMQLT", "Quilted Changing Mat", HUSHWELL, 20.0,
       "A quilted cotton mat that folds flat, with no pockets.",
       (GREY, GREEN, RED), False, 0, "Standard"),
    _m("NYMWPL", "Large Wipe-Clean Changing Mat", DOVECOTE, 14.0,
       "A large wipe-clean mat with raised edges, easy to rinse and dry.",
       (BLACK, SAGE, CREAM), True, 0, "Large"),
    _m("NYMQPK", "Quilted Changing Mat with Side Pockets", THISTLE, 24.0,
       "A quilted mat with two side pockets and a carry handle.",
       (NAVY, WHITE, RED), False, 2, "Large"),
)  # fmt: skip

SPEC = TypeSpec(
    key="changing_mat",
    department="Home",
    product_type="Changing Mat",
    rows=_ROWS,
    decoys=(
        decoy(1, "red changing mat", _ROWS[0], 5, "Red Trim Wipe-Clean Changing Mat",
              "A blue mat with a red binding round the edge; the mat is blue.", color=BLUE),
        decoy(4, "waterproof changing mat", _ROWS[1], 6, "Waterproof Quilted Changing Mat",
              "A quilted cotton mat that is not waterproof: wipe it with a damp cloth only.",
              color=GREY),
        decoy(2, "changing bag", _ROWS[2], 7, "Changing Bag Mat Wipe-Clean",
              "A wipe-clean mat that clips onto a pram. It is a mat, not a bag.",
              color=BLACK),
        decoy(6, "bear", _ROWS[3], 8, "Bear Hill Quilted Changing Mat",
              "From the Bear Hill range, named after a village; there is no bear on the mat.",
              color=NAVY),
    ),
)  # fmt: skip
