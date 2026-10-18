"""Hex Key Bit Socket Set: a text-match decoy for the industrial seed queries (#462).

A socket set of hex key bits on a ratchet. Its title holds the seed noun and its category path does
not, so it shows what a category policy removes (the seeds it serves are in
``domains/industrial/seed_decoys.py``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.typespec import TypeSpec
from synthetic_ecommerce_data.domains.industrial.breadth import BreadthRow

SPEC = TypeSpec(
    "bit_socket_sets",
    label="Hex Key Bit Socket Set",
    breadth=BreadthRow(
        key="bit_socket_sets",
        category=("Hand Tools", "Sockets & Ratchets", "Bit Socket Sets"),
        family="hand_tool",
        shape="cylinder",
        item="Hex Key Bit Socket Set",
        descriptor_attr=None,
        size_attr="Drive Size",
        size_values=("3/8 in", "1/2 in"),
        attributes={"Material": ("Chrome Vanadium Steel",)},
        price_range=(15.0, 60.0),
        skus=2,
        featured_sizes=(),
        reason=(
            "decoy for the industrial seed queries (#462): a socket set of hex key bits on a "
            "ratchet"
        ),
    ),
)
