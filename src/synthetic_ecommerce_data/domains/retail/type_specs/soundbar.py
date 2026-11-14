"""Soundbars (gen#956): Electronics > Audio > Soundbars.

A breadth type: ``derivable`` True, so the scaled build draws more soundbars from these rows by
the values their titles show (channels, connection and profile). The bar's fabric is the SKU's
color; ``channels`` draws a driver per front channel and, for a ``.1``, a subwoofer box beside
the bar (:func:`kit_audio.soundbar`). Four title patterns, each by two brands.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.audio_rows import BLACK, SOUNDBARS, decoy, row
from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    ELECTRONICS_OWNERS,
    HALVERN,
    MARRICK,
    MERVANE,
    NIMBREL,
    PELLIMAR,
    QUORRIN,
    TORVANE,
    WEXMOOR,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

DEPARTMENT = "Electronics"


def _sb(code: str, title: str, brand: str, price: float, description: str, channels: str,
        link: str, profile: str) -> object:  # fmt: skip
    attrs = (a("channels", "Channels", channels), a("connectivity", "Connectivity", link),
             a("profile", "Profile", profile))  # fmt: skip
    return row(code, title, brand, SOUNDBARS, "Soundbar", "soundbar", price, description, attrs,
               (("channels", channels),))  # fmt: skip


ROWS = (
    _sb("AUB001", "2.1 Channel Bluetooth Soundbar", MARRICK, 149.0,
        "Clear dialogue and a deep low end under the TV, with a remote in the box.", "2.1", "Bluetooth", "Compact"),
    _sb("AUB002", "5.1 Channel Wi-Fi Soundbar", HALVERN, 399.0,
        "Cinema sound from one bar, with app control and night mode.", "5.1", "Wi-Fi", "Full-Size"),
    _sb("AUB003", "Slim 3.1 Channel Soundbar", WEXMOOR, 279.0,
        "A center channel for voices and a bar that sits flat below a wall-mounted TV.", "3.1", "Optical", "Slim"),
    _sb("AUB004", "Compact 2.0 Channel Soundbar", NIMBREL, 89.0,
        "A small bar for a bedroom TV, with one cable to set up.", "2.0", "Bluetooth", "Compact"),
    _sb("AUB005", "Slim Bluetooth Soundbar", TORVANE, 129.0,
        "Stream music from a phone and switch to the TV with one button.", "2.0", "Bluetooth", "Slim"),
    _sb("AUB006", "Full-Size Optical Soundbar", QUORRIN, 199.0,
        "A wide bar for a large screen, with a dialogue mode and wall brackets.", "3.1", "Optical", "Full-Size"),
    _sb("AUB007", "Compact 2.1 Channel Wi-Fi Soundbar", PELLIMAR, 229.0,
        "Multi-room music over the home network and a deep low end for films.", "2.1", "Wi-Fi", "Compact"),
    _sb("AUB008", "Full-Size 5.1 Channel Optical Soundbar", MERVANE, 349.0,
        "Five front and side channels for films and games, with a learning remote.", "5.1", "Optical", "Full-Size"),
)  # fmt: skip

SPEC = TypeSpec(
    key="soundbar",
    department=DEPARTMENT,
    product_type="Soundbar",
    derivable=True,
    owners=ELECTRONICS_OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "white soundbar", "vocabulary", decoy(ROWS[0], "AUBWRM", "2.1 Channel Bluetooth Soundbar with White Remote",
              "A black soundbar and subwoofer, with a white remote that is easy to find.", BLACK)),
        Decoy(6, "red soundbar", "generic", decoy(ROWS[2], "AUBRRK", "Red Rock Slim 3.1 Channel Soundbar",
              "From the Red Rock range: a slim soundbar in black for a wall-mounted TV.", BLACK)),
    ),
)  # fmt: skip
