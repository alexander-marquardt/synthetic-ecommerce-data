"""Gaming headsets (gen#956, slice 2b): Electronics > Gaming > Gaming Headsets.

A breadth type: ``derivable`` True, so the scaled build draws more headsets from these rows by
the values their titles show (a connection, a sound, a feature, or a connection and a sound).
The headband and cups are the SKU's color, and ``connection`` draws a cable and plug or a power
light (:func:`kit_gaming.gaming_headset`). The key and name of ``connection`` are the ones the
Electronics earbuds use. Four title patterns, each by two brands.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    ARDMOOR,
    CINDREL,
    DUNVALE,
    ELECTRONICS_OWNERS,
    HALVERN,
    MARRICK,
    NIMBREL,
    QUORRIN,
    WEXMOOR,
)
from synthetic_ecommerce_data.domains.retail.gaming_rows import (
    BLACK,
    HEADSETS,
    WHITE,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

DEPARTMENT = "Electronics"


def _gh(code: str, title: str, brand: str, price: float, description: str, link: str,
        sound: str, feature: str) -> object:  # fmt: skip
    attrs = (a("connection", "Connection", link), a("headset_sound", "Sound", sound),
             a("headset_feature", "Headset feature", feature))  # fmt: skip
    return row(code, title, brand, HEADSETS, "Gaming Headset", "gaming_headset", price,
               description, attrs, (("connection", link.lower()),))  # fmt: skip


ROWS = (
    _gh("GMH001", "Wireless Gaming Headset", WEXMOOR, 89.0,
        "A low-delay dongle, thirty hours per charge and a mic that flips up to mute.", "Wireless", "Stereo", "Noise Cancelling Mic"),
    _gh("GMH002", "Wired Gaming Headset", CINDREL, 35.0,
        "One plug for a console pad or a PC, and a volume wheel on the ear cup.", "Wired", "Stereo", "Memory Foam Cushions"),
    _gh("GMH003", "7.1 Surround Gaming Headset", ARDMOOR, 79.0,
        "Hear footsteps behind and to the side, with large drivers and a padded band.", "Wired", "7.1 Surround", "RGB Lighting"),
    _gh("GMH004", "Stereo Gaming Headset", DUNVALE, 29.0,
        "A light frame and a clear mic for team chat, for long evenings of play.", "Wireless", "Stereo", "Memory Foam Cushions"),
    _gh("GMH005", "Gaming Headset with Noise Cancelling Mic", QUORRIN, 69.0,
        "A boom mic that filters out keyboard clicks and the room around it.", "Wired", "7.1 Surround", "Noise Cancelling Mic"),
    _gh("GMH006", "Gaming Headset with RGB Lighting", NIMBREL, 59.0,
        "Lit rings on both ear cups that cycle through effects set in the app.", "Wireless", "Stereo", "RGB Lighting"),
    _gh("GMH007", "Wireless 7.1 Surround Gaming Headset", HALVERN, 129.0,
        "A wide sound stage, a detachable mic and a charging stand in the box.", "Wireless", "7.1 Surround", "Noise Cancelling Mic"),
    _gh("GMH008", "Wired Stereo Gaming Headset", MARRICK, 39.0,
        "A steel band, soft cushions and an in-line mute switch on the cable.", "Wired", "Stereo", "Memory Foam Cushions"),
)  # fmt: skip

SPEC = TypeSpec(
    key="gaming_headset",
    department=DEPARTMENT,
    product_type="Gaming Headset",
    derivable=True,
    owners=ELECTRONICS_OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "green gaming headset", "vocabulary", decoy(ROWS[2], "GMHGRL", "7.1 Surround Gaming Headset with Green Ring Lights",
              "A black gaming headset whose ear cups are ringed with green lights.", BLACK)),
        Decoy(6, "yellow gaming headset", "generic", decoy(ROWS[3], "GMHYPK", "Yellow Peak Stereo Gaming Headset",
              "From the Yellow Peak range: a stereo gaming headset in white.", WHITE)),
    ),
)  # fmt: skip
