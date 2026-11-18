"""Blood-pressure monitors (gen#968, slice 2): Health > Health Monitors > Blood Pressure Monitors.

A breadth type (``derivable``): the scaled build draws more monitors by swapping the fit and
the display the title shows. Each style is one SKU. The drawing is a desk unit with its arm cuff,
or a wrist unit on its cuff, by the row's fit (:func:`kit_health.bp_monitor`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.health_rows import (
    GREY,
    HALVERING,
    MONITORS,
    OWNERS,
    QUELLMOOR,
    THRENNICK,
    WHITE,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_PATH = (*MONITORS, "Blood Pressure Monitors")


def _monitor(code, title, brand, fit, display, price, desc, color=WHITE) -> object:  # noqa: ANN001
    return row(code, title, brand, _PATH, "Blood Pressure Monitors", "bp_monitor", desc,
               (a("fit", "Fit", fit), a("display", "Display", display)), ("fit", fit.lower()),
               price=price, color=color)  # fmt: skip


ROWS = (
    _monitor("HBPUPA", "Upper Arm Blood Pressure Monitor", THRENNICK, "Upper Arm", "Plain", 30.0,
             "Reads blood pressure and pulse at one press of a button, with a soft cuff and large digits."),
    _monitor("HBPUPB", "Backlit Upper Arm Blood Pressure Monitor", QUELLMOOR, "Upper Arm", "Backlit", 42.0,
             "A lit display, a soft cuff and a memory of 60 readings for each of two users.", GREY),
    _monitor("HBPWRS", "Wrist Blood Pressure Monitor", HALVERING, "Wrist", "Plain", 25.0,
             "A compact monitor on its own cuff, with a travel case and a memory of 60 readings."),
    _monitor("HBPWRB", "Backlit Wrist Blood Pressure Monitor", THRENNICK, "Wrist", "Backlit", 34.0,
             "A compact monitor with a lit display, its own cuff and a travel case.", GREY),
    _monitor("HBPUP2", "Two User Upper Arm Blood Pressure Monitor", HALVERING, "Upper Arm", "Backlit", 48.0,
             "Two user buttons, each with its own memory of 90 readings, a soft cuff and a plug-in power adapter."),
)  # fmt: skip

#: Text-match decoys: the title names a range holding the query's word, the fields say another
#: fit, so only a policy that reads ``fit`` puts the real monitors first.
DECOYS = (
    Decoy(6, "wrist blood pressure monitor", "generic", decoy(
        ROWS[0], "HBPDY1", "Wrist Ease Upper Arm Blood Pressure Monitor",
        "From the Wrist Ease range: an upper-arm monitor with a soft cuff and large digits.")),
    Decoy(6, "upper arm blood pressure monitor", "generic", decoy(
        ROWS[2], "HBPDY2", "Upper Deck Wrist Blood Pressure Monitor",
        "From the Upper Deck range: a compact wrist monitor with a travel case.")),
)  # fmt: skip

SPEC = TypeSpec(
    key="blood_pressure_monitors",
    department="Health",
    product_type="Blood Pressure Monitors",
    derivable=True,
    owners=OWNERS,
    rows=ROWS,
    decoys=DECOYS,
)
