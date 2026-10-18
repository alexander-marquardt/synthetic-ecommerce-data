"""Hex Bit Socket Set for M12x1.75 Socket Cap Screws: a text-match decoy for the industrial seed queries (#462).

A hex bit socket set that drives M12x1.75 socket cap screws. Its title holds the seed noun and its category path does not, so it
shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "hex_bit_socket_sets",
    label="Hex Bit Socket Set for M12x1.75 Socket Cap Screws",
    breadth=BreadthRow(
        key="hex_bit_socket_sets",
        category=("Hand Tools", "Sockets & Ratchets", "Hex Bit Socket Sets"),
        family="hand_tool",
        shape="cylinder",
        item="Hex Bit Socket Set for M12x1.75 Socket Cap Screws",
        descriptor_attr=None,
        size_attr="Drive Size",
        size_values=("3/8 in", "1/2 in"),
        attributes={"Material": ("Chrome Vanadium Steel",), "Finish": ("Chrome Plated",)},
        price_range=(18.0, 70.0),
        skus=2,
        featured_sizes=(),
        reason="decoy for the industrial seed queries (#462): a hex bit socket set that drives M12x1.75 socket cap screws",
    ),
)
