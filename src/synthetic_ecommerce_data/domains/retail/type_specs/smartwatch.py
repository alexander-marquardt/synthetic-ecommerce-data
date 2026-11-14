"""Smartwatches (gen#956, slice 3a): Electronics > Wearables > Smartwatches.

A breadth type: ``derivable`` True, so the scaled build draws more smartwatches from these rows by
the values their titles show (a face, a feature, a network, or a face and a network). The strap
is the SKU's color. ``smartwatch_face`` draws a round or a square case, and
``smartwatch_network`` draws a map pin on the screen for GPS or a red crown for cellular
(:func:`kit_gadgets.smartwatch`). Four title patterns, each by two brands. ``Fitness Band``, the
Womens and Mens ``Watches`` type of gen#423, stays where it is.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    ARDMOOR,
    BOLTWICK,
    CINDREL,
    ELECTRONICS_OWNERS,
    HALVERN,
    MERVANE,
    PELLIMAR,
    TORVANE,
    WEXMOOR,
)
from synthetic_ecommerce_data.domains.retail.gadgets_rows import (
    BLACK,
    SMARTWATCHES,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

DEPARTMENT = "Electronics"


def _sw(code: str, title: str, brand: str, price: float, description: str, face: str,
        network: str, feature: str) -> object:  # fmt: skip
    attrs = (a("smartwatch_face", "Smartwatch face", face),
             a("smartwatch_network", "Smartwatch network", network),
             a("smartwatch_feature", "Smartwatch feature", feature))  # fmt: skip
    return row(code, title, brand, SMARTWATCHES, "Smartwatch", "smartwatch", price, description,
               attrs, (("smartwatch_face", face.lower()), ("smartwatch_network", network.lower())))  # fmt: skip


ROWS = (
    _sw("SMW001", "Round Smartwatch", HALVERN, 199.0,
        "A classic round face with messages, timers and a week of battery.", "Round", "GPS", "Heart Rate Monitor"),
    _sw("SMW002", "Square Smartwatch", TORVANE, 179.0,
        "A bright square screen that shows a full message without scrolling.", "Square", "GPS", "Sleep Tracking"),
    _sw("SMW003", "Smartwatch with Heart Rate Monitor", PELLIMAR, 149.0,
        "Checks your pulse all day and warns you when it stays high at rest.", "Round", "GPS", "Heart Rate Monitor"),
    _sw("SMW004", "Smartwatch with Sleep Tracking", WEXMOOR, 129.0,
        "Scores each night's sleep and wakes you gently with a vibration.", "Square", "GPS", "Sleep Tracking"),
    _sw("SMW005", "GPS Smartwatch", BOLTWICK, 229.0,
        "Maps your runs and rides on its own, with the phone left at home.", "Round", "GPS", "Heart Rate Monitor"),
    _sw("SMW006", "Cellular Smartwatch", CINDREL, 329.0,
        "Takes calls and streams music on its own mobile connection.", "Square", "Cellular", "Heart Rate Monitor"),
    _sw("SMW007", "Round GPS Smartwatch", ARDMOOR, 249.0,
        "A sports watch with a steel bezel, route maps and a two week battery.", "Round", "GPS", "Sleep Tracking"),
    _sw("SMW008", "Square Cellular Smartwatch", MERVANE, 349.0,
        "Calls, texts and payments from the wrist, with the phone left behind.", "Square", "Cellular", "Sleep Tracking"),
)  # fmt: skip

SPEC = TypeSpec(
    key="smartwatch",
    department=DEPARTMENT,
    product_type="Smartwatch",
    derivable=True,
    owners=ELECTRONICS_OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "red smartwatch", "vocabulary", decoy(ROWS[5], "SMWRDC", "Cellular Smartwatch with Red Crown",
              "A black cellular smartwatch whose crown is ringed in red.", BLACK)),
        Decoy(6, "white smartwatch", "generic", decoy(ROWS[4], "SMWWPK", "White Peak GPS Smartwatch",
              "From the White Peak range: a GPS smartwatch in black.", BLACK)),
    ),
)  # fmt: skip
