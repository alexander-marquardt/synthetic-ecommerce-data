"""Smart plugs (gen#956): Electronics > Smart Home > Smart Plugs.

A breadth type: ``derivable`` True, so the scaled build draws more plugs from these rows by the
values their titles show (a form, a connection or a feature, or a form and a connection). The
body is the SKU's color; ``plug_form`` draws a mini plug, a dual outlet or an outdoor plug with its cover and cable
(:func:`kit_smart_home.smart_plug`). Four title patterns, each by two brands.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    BOLTWICK,
    CINDREL,
    ELECTRONICS_OWNERS,
    HALVERN,
    MARRICK,
    NIMBREL,
    QUORRIN,
    TORVANE,
    WEXMOOR,
)
from synthetic_ecommerce_data.domains.retail.smart_home_rows import BLACK, PLUGS, WHITE, decoy, row
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

DEPARTMENT = "Electronics"


def _sp(code: str, title: str, brand: str, price: float, description: str, form: str,
        link: str, feature: str) -> object:  # fmt: skip
    attrs = (a("plug_form", "Plug form", form), a("connectivity", "Connectivity", link),
             a("plug_feature", "Plug feature", feature))  # fmt: skip
    return row(code, title, brand, PLUGS, "Smart Plug", "smart_plug", price, description, attrs,
               (("plug_form", form.lower()),))  # fmt: skip


ROWS = (
    _sp("SMP001", "Mini Smart Plug with App Control", MARRICK, 19.0,
        "A small plug that leaves the next socket free, switched from a phone.", "Mini", "Wi-Fi", "Energy Monitoring"),
    _sp("SMP002", "Dual Outlet Smart Plug with App Control", CINDREL, 29.0,
        "Two sockets each switched on its own, from the app or on a schedule.", "Dual Outlet", "Zigbee", "Scheduling"),
    _sp("SMP003", "Wi-Fi Smart Plug", WEXMOOR, 17.0,
        "Turn a kettle or a fan on from anywhere, with no hub to set up.", "Mini", "Wi-Fi", "Voice Control"),
    _sp("SMP004", "Zigbee Smart Plug", BOLTWICK, 15.0,
        "A plug that joins a smart hub and repeats its signal to the next room.", "Mini", "Zigbee", "Scheduling"),
    _sp("SMP005", "Smart Plug with Energy Monitoring", NIMBREL, 22.0,
        "Track a washing machine's power use and get a message when it ends.", "Dual Outlet", "Zigbee", "Energy Monitoring"),
    _sp("SMP006", "Smart Plug with Voice Control", QUORRIN, 18.0,
        "Ask a speaker to switch a lamp, or group plugs into one room scene.", "Mini", "Wi-Fi", "Voice Control"),
    _sp("SMP007", "Outdoor Wi-Fi Smart Plug", TORVANE, 32.0,
        "A weather cover and a short cable for garden lights and a pond pump.", "Outdoor", "Wi-Fi", "Scheduling"),
    _sp("SMP008", "Mini Zigbee Smart Plug", HALVERN, 16.0,
        "A compact plug for a hub, with a button to switch it by hand.", "Mini", "Zigbee", "Energy Monitoring"),
)  # fmt: skip

SPEC = TypeSpec(
    key="smart_plug",
    department=DEPARTMENT,
    product_type="Smart Plug",
    derivable=True,
    owners=ELECTRONICS_OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "red smart plug", "vocabulary", decoy(ROWS[0], "SMPRSL", "Mini Smart Plug with App Control and Red Status Light",
              "A white mini plug whose status light glows red while the socket is off.", WHITE)),
        Decoy(6, "yellow smart plug", "generic", decoy(ROWS[6], "SMPYBR", "Yellow Brick Outdoor Wi-Fi Smart Plug",
              "From the Yellow Brick range: an outdoor smart plug in black.", BLACK)),
    ),
)  # fmt: skip
