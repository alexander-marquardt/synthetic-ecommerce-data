"""Home furnishing and decor: the options each spec declares (gen#413, gen#1183)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Option

from ._shared import DROP

MOVED: dict[str, list[Option]] = {
    "curtains": [DROP],
    "blind": [DROP],
    "shower_curtain": [DROP],
    # The options the shared table still held that no shared source's row carries (#413).
    "wallpaper": [Option("roll_length_m", "roll_length", "Roll length", "MTR")],
    # a grouped sofa's version and what follows it (gen#808)
    "sofa": [
        Option("configuration", "configuration", "Configuration"),
        Option("seat_count", "seat_count", "Seat count", "C62"),
        Option("depth_cm", "item_depth", "Item depth", "CMT"),
    ],
}
