"""Baby blankets (gen#213): cellular, fleece, knitted and swaddle blankets, pram or cot sized,
drawn by :func:`kit_baby.baby_blanket` with the weave and the size they state. A blanket's
SKUs are its colors. Hand-authored text-match decoys sit in the same node."""

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

_L = "Baby Blankets"


def _b(code, title, brand, price, desc, colors, kind, size, fabric):  # fmt: skip
    return nursery(
        code, title, brand, _L, "Baby Blanket", "baby_blanket", price, desc, colors,
        (a("blanket_type", "Blanket type", kind), a("blanket_size", "Blanket size", size),
         a("fabric", "Fabric", fabric)),
        (("type", {"Knitted": "knit"}.get(kind, kind.lower())), ("size", size.lower())),
    )  # fmt: skip


_ROWS = (
    _b("NYBCEL", "Cellular Baby Blanket for a Pram", FENWOLD, 9.0,
       "A breathable cotton cellular blanket in a pram size, for layering up or down.",
       (WHITE, BLUE, PINK, YELLOW), "Cellular", "Pram", "Cotton"),
    _b("NYBFLC", "Soft Fleece Baby Blanket for a Cot", HUSHWELL, 12.0,
       "A cot size fleece blanket with a stitched edge, soft against the skin.",
       (GREEN, RED, GREY), "Fleece", "Cot", "Fleece"),
    _b("NYBKNT", "Chunky Knitted Baby Blanket", DOVECOTE, 22.0,
       "A hand-finished knitted blanket in a pram size, in a chunky stitch.",
       (CREAM, SAGE, BLACK), "Knitted", "Pram", "Cotton"),
    _b("NYBSWD", "Muslin Swaddle Baby Blanket", THISTLE, 14.0,
       "A cot size muslin swaddle wrap that folds over a newborn.",
       (WHITE, YELLOW, BLUE), "Swaddle", "Cot", "Muslin"),
)  # fmt: skip

SPEC = TypeSpec(
    key="baby_blanket",
    department="Home",
    product_type="Baby Blanket",
    rows=_ROWS,
    decoys=(
        decoy(1, "blue baby blanket", _ROWS[0], 1, "Blue Trim Cellular Baby Blanket",
              "A white cellular blanket with a blue satin binding; the blanket itself is white.",
              color=WHITE),
        decoy(3, "cot bed blanket", _ROWS[1], 2, "Cot Bed Print Fleece Baby Blanket",
              "A pram size fleece blanket printed with a small cot bed pattern.",
              attrs=(a("blanket_type", "Blanket type", "Fleece"),
                     a("blanket_size", "Blanket size", "Pram"), a("fabric", "Fabric", "Fleece")),
              color=GREEN),
        decoy(6, "sheep", _ROWS[2], 3, "Little Sheep Knitted Baby Blanket",
              "From the Little Sheep range, named for the farm; the wool-free cotton knit has no "
              "sheep on it.",
              color=CREAM),
        decoy(7, "dovecote", _ROWS[3], 4, "Dovecote Lane Swaddle Baby Blanket",
              "A muslin swaddle from Dovecote Lane; the name is the maker's, not a bird house.",
              brand=DOVECOTE, color=YELLOW),
    ),
)  # fmt: skip
