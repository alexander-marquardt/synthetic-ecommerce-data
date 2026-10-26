"""Tool kits (gen#191, the issue's comment): a hammer, screwdrivers, pliers and a tape, with sockets in
the larger kits. The piece count is a counted entry the title states; :func:`kit_drills.tool_kit`
draws a case or a bag."""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import diy_tools as d
from breadth_rows import Contents
from type_registry import TypeSpec, a

#: What each kit holds: the one source of its piece count, its title and its description.
K6 = Contents(
    (1, "claw hammer"), (2, "screwdrivers"), (1, "pair of pliers"), (1, "tape measure"), (1, "bag")
)
K24 = Contents(
    (1, "claw hammer"),
    (6, "screwdrivers"),
    (2, "pairs of pliers"),
    (1, "tape measure"),
    (1, "adjustable wrench"),
    (12, "sockets"),
    (1, "case"),
)
K40 = Contents(
    (1, "claw hammer"),
    (4, "screwdrivers"),
    (2, "pairs of pliers"),
    (1, "tape measure"),
    (1, "adjustable wrench"),
    (30, "sockets"),
    (1, "case"),
)
K61 = Contents(
    (1, "claw hammer"),
    (8, "screwdrivers"),
    (3, "pairs of pliers"),
    (1, "tape measure"),
    (1, "adjustable wrench"),
    (40, "sockets"),
    (1, "ratchet"),
    (5, "hex keys"),
    (1, "case"),
)


def _row(code, brand, price, c, text, case):
    return (code, c.title("Tool Kit"), brand, price, c.text(text),
            (a("kit_contents", "Contents", "Hammer, screwdrivers, pliers, tape measure and sockets" if c.n > 6 else "Hammer, screwdrivers, pliers and tape measure"),
             a("case", "Case", "Soft bag" if case == "bag" else "Hard case"), *c.attrs),
            (("case", case),))  # fmt: skip


ROWS = d.styles(
    (
        _row("TKT006", d.BRI, 12.0, K6, "A starter kit for the first flat, in a soft bag.", "bag"),
        _row(
            "TKT024",
            d.TOR,
            29.0,
            K24,
            "A household kit with a ratchet socket set, in a hard case.",
            "case",
        ),
        _row(
            "TKT040",
            d.HAR,
            39.0,
            K40,
            "A household kit with a deep socket range, in a hard case.",
            "case",
        ),
        _row(
            "TKT061",
            d.CAL,
            59.0,
            K61,
            "A workshop kit with a ratchet and hex keys, in a hard case.",
            "case",
        ),
    ),
    "Tool Kit",
    "tool_kit",
    d.TOOL_SETS + ("Tool Kits",),
)

SPEC = TypeSpec(
    key="tool_kit",
    department=d.HOME,
    product_type="Tool Kit",
    rows=ROWS,
    decoys=d.decoys(ROWS[0], "tool kit", ("DCTKCS", "Tool Kit, Case Free", "tool kit with case")),
    owners=d.OWNERS,
)
