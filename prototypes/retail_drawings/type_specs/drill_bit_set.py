"""Drill bit sets (gen#191, the issue's comment): a retail set of drill bits, never a plain "Drill".

The material it drills into, the shank (round, hex, SDS) and the piece count are structured entries,
and the title states the count. :func:`kit_drills.drill_bit_set` draws the shank and the bits."""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import diy_tools as d
from breadth_rows import Contents
from type_registry import TypeSpec, a

#: What each set holds: the one source of its piece count, its title and its description.
WOOD = Contents((16, "brad point bits"), (2, "countersinks"), (1, "case"))
MASONRY = Contents((12, "masonry bits"), (1, "case"))
METAL = Contents((18, "HSS metal bits"), (1, "case"))
MULTI = Contents((25, "wood bits"), (8, "masonry bits"), (8, "HSS metal bits"), (1, "case"))
SDS = Contents((5, "SDS-plus bits"), (1, "case"))
HEX = Contents((10, "hex shank bits"), (1, "case"))


def _row(code, name, brand, price, c, drills, shank, bits, text):
    """``drills`` is one material or a tuple: a multi-purpose set states each material it drills into."""
    into = (drills,) if isinstance(drills, str) else drills
    return (code, c.title(name), brand, price, c.text(text),
            (*(a("drills_into", "Drills into", m) for m in into), a("shank", "Shank", shank), a("case", "Case", "Hard case"), *c.attrs),
            (("shank", shank.lower()), ("bits", str(bits))))  # fmt: skip


ROWS = d.styles(
    (
        _row(
            "BTWD19",
            "Wood Drill Bit Set",
            d.TOR,
            11.0,
            WOOD,
            "Wood",
            "Round",
            9,
            "Ground points that start cleanly, in a hard case.",
        ),
        _row(
            "BTMS13",
            "Masonry Drill Bit Set",
            d.STO,
            12.0,
            MASONRY,
            "Masonry",
            "Round",
            12,
            "Carbide tips for brick, block and stone, in a hard case.",
        ),
        _row(
            "BTHS19",
            "HSS Metal Drill Bit Set",
            d.BRI,
            14.0,
            METAL,
            "Metal",
            "Round",
            13,
            "Titanium-coated steel for sheet and bar, in a hard case.",
        ),
        _row(
            "BTMP42",
            "Multi-Purpose Drill Bit Set",
            d.HAR,
            24.0,
            MULTI,
            ("Multi-purpose", "Wood", "Masonry", "Metal"),
            "Round",
            13,
            "Bits for wood, masonry and metal, in a hard case.",
        ),
        _row(
            "BTSD06",
            "SDS-Plus Masonry Drill Bit Set",
            d.TOR,
            21.0,
            SDS,
            "Masonry",
            "SDS",
            5,
            "Four-cutter tips for concrete, in a hard case.",
        ),
        _row(
            "BTHX11",
            "Hex Shank Drill Bit Set",
            d.CAL,
            13.0,
            HEX,
            "Multi-purpose",
            "Hex",
            10,
            "A quarter-inch hex shank for impact drivers, in a hard case.",
        ),
    ),
    "Drill Bit Set",
    "drill_bit_set",
    d.TOOL_SETS + ("Drill Bit Sets",),
)

SPEC = TypeSpec(
    key="drill_bit_set",
    department=d.HOME,
    product_type="Drill Bit Set",
    rows=ROWS,
    decoys=d.decoys(
        ROWS[0], "drill bit set", ("DCBSMS", "Drill Bit Set, Masonry Free", "masonry drill bit set")
    ),
    owners=d.OWNERS,
)
