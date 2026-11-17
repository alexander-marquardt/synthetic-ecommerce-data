"""Headphones (gen#956): Electronics > Audio > Headphones.

A breadth type: ``derivable`` True, so the scaled build draws more headphones from these rows by
the values their titles show (connection, fit and sound feature). The cups are the SKU's color;
``fit`` draws large over-ear cups or small on-ear pads and ``connection`` a cable with its plug
or a power light (:func:`kit_audio.headphones`). Four title patterns, each by two brands.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.audio_rows import BLACK, HEADPHONES, WHITE, decoy, row
from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    ARDMOOR,
    BOLTWICK,
    CINDREL,
    ELECTRONICS_OWNERS,
    HALVERN,
    MARRICK,
    NIMBREL,
    TORVANE,
    WEXMOOR,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

DEPARTMENT = "Electronics"


def _hp(code: str, title: str, brand: str, price: float, description: str, connection: str,
        fit: str, feature: str) -> object:  # fmt: skip
    attrs = (a("connection", "Connection", connection), a("fit", "Fit", fit),
             a("sound_feature", "Sound feature", feature))  # fmt: skip
    params = (("fit", fit.lower()), ("connection", connection.lower()))
    return row(code, title, brand, HEADPHONES, "Headphones", "headphones", price, description,
               attrs, params)  # fmt: skip


ROWS = (
    _hp("AUH001", "Wireless Over-Ear Noise Cancelling Headphones", WEXMOOR, 129.0,
        "Cushioned cups and a padded band, with thirty hours of play per charge.", "Wireless", "Over-Ear", "Noise Cancelling"),
    _hp("AUH002", "Wired On-Ear Studio Headphones", MARRICK, 69.0,
        "A flat, even sound for mixing and a swivel cup for one-ear listening.", "Wired", "On-Ear", "Studio"),
    _hp("AUH003", "Foldable Wired On-Ear Headphones", ARDMOOR, 25.0,
        "Light headphones that fold flat into a bag, with soft pads for long listening.", "Wired", "On-Ear", "Bass Boost"),
    _hp("AUH004", "Foldable Wireless Over-Ear Headphones", CINDREL, 59.0,
        "Headphones that fold into their pouch, with a quick charge for a day out.", "Wireless", "Over-Ear", "Hi-Res"),
    _hp("AUH005", "Bass Boost Wireless Headphones", BOLTWICK, 45.0,
        "A deep, punchy low end and controls on the cup to skip and pause.", "Wireless", "On-Ear", "Bass Boost"),
    _hp("AUH006", "Hi-Res USB-C Headphones", HALVERN, 89.0,
        "Plug straight into a laptop or a phone for detailed sound with no adapter.", "USB-C", "Over-Ear", "Hi-Res"),
    _hp("AUH007", "Over-Ear Bass Boost Headphones with Microphone", TORVANE, 39.0,
        "A clear boom-free mic for calls and a band that adjusts to any head.", "Wired", "Over-Ear", "Bass Boost"),
    _hp("AUH008", "On-Ear Noise Cancelling Headphones with Microphone", NIMBREL, 99.0,
        "Quiet calls on the move, with a slim band and pads that rest on the ear.", "Wireless", "On-Ear", "Noise Cancelling"),
)  # fmt: skip

SPEC = TypeSpec(
    key="headphones",
    department=DEPARTMENT,
    product_type="Headphones",
    derivable=True,
    owners=ELECTRONICS_OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "red headphones", "vocabulary", decoy(ROWS[0], "AUHRDC", "Red Cushion Wireless Over-Ear Headphones",
              "Black wireless headphones with red ear cushions and a matching band.", BLACK)),
        Decoy(6, "blue headphones", "generic", decoy(ROWS[1], "AUHBLH", "Blue Harbor Wired On-Ear Headphones",
              "From the Blue Harbor range: wired on-ear headphones in white.", WHITE)),
    ),
)  # fmt: skip
