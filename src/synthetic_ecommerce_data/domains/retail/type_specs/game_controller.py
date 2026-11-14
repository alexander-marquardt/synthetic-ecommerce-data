"""Game controllers (gen#956, slice 2b): Electronics > Gaming > Game Controllers.

A breadth type: ``derivable`` True, so the scaled build draws more controllers from these rows by
the values their titles show (a form, a connection, a feature, or a form and a connection). The
body is the SKU's color. ``controller_form`` draws a classic pad, a pro pad with triggers and
back paddles, or two grips around a phone, and ``connection`` draws a cable or a lit bar
(:func:`kit_gaming.game_controller`). Four title patterns, each by two brands.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    ARDMOOR,
    BOLTWICK,
    DASKEL,
    ELECTRONICS_OWNERS,
    MERVANE,
    NIMBREL,
    PELLIMAR,
    QUORRIN,
    TORVANE,
)
from synthetic_ecommerce_data.domains.retail.gaming_rows import (
    BLACK,
    CONTROLLERS,
    WHITE,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

DEPARTMENT = "Electronics"


def _gc(code: str, title: str, brand: str, price: float, description: str, form: str,
        link: str, feature: str) -> object:  # fmt: skip
    attrs = (a("controller_form", "Controller form", form), a("connection", "Connection", link),
             a("controller_feature", "Controller feature", feature))  # fmt: skip
    return row(code, title, brand, CONTROLLERS, "Game Controller", "game_controller", price,
               description, attrs, (("controller_form", form.lower()), ("connection", link.lower())))  # fmt: skip


ROWS = (
    _gc("GMC001", "Pro Game Controller", QUORRIN, 69.0,
        "Two triggers with short travel and two paddles on the back for fast reloads.", "Pro", "Wireless", "Remappable Buttons"),
    _gc("GMC002", "Mobile Game Controller", PELLIMAR, 45.0,
        "Grips that clip either side of a phone, with sticks for console-style play.", "Mobile", "Wired", "Hall Effect Sticks"),
    _gc("GMC003", "Wireless Game Controller", TORVANE, 49.0,
        "Forty hours of play per charge and a low-delay link to a PC or a console.", "Classic", "Wireless", "Hall Effect Sticks"),
    _gc("GMC004", "Wired Game Controller", BOLTWICK, 25.0,
        "A ten foot cable, so it never needs a charge, for a PC or a console.", "Classic", "Wired", "Remappable Buttons"),
    _gc("GMC005", "Game Controller with Hall Effect Sticks", ARDMOOR, 59.0,
        "Magnetic sticks that do not drift, and a textured grip for long sessions.", "Classic", "Wireless", "Hall Effect Sticks"),
    _gc("GMC006", "Game Controller with Remappable Buttons", NIMBREL, 55.0,
        "Map any move to a back button and save four profiles on the pad itself.", "Pro", "Wired", "Remappable Buttons"),
    _gc("GMC007", "Pro Wireless Game Controller", DASKEL, 79.0,
        "Swappable stick caps, trigger stops and a charging dock in the box.", "Pro", "Wireless", "Hall Effect Sticks"),
    _gc("GMC008", "Classic Wired Game Controller", MERVANE, 29.0,
        "A familiar layout with a full d-pad, for retro games and racing alike.", "Classic", "Wired", "Hall Effect Sticks"),
)  # fmt: skip

SPEC = TypeSpec(
    key="game_controller",
    department=DEPARTMENT,
    product_type="Game Controller",
    derivable=True,
    owners=ELECTRONICS_OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "red game controller", "vocabulary", decoy(ROWS[0], "GMCRDT", "Pro Game Controller with Red Trigger Buttons",
              "A black pro controller whose two triggers are picked out in red.", BLACK)),
        Decoy(6, "blue game controller", "generic", decoy(ROWS[3], "GMCBHB", "Blue Harbor Wired Game Controller",
              "From the Blue Harbor range: a wired game controller in white.", WHITE)),
    ),
)  # fmt: skip
