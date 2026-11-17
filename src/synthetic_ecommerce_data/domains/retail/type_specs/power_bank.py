"""Power banks (gen#956, slice 3a): Electronics > Accessories > Power Banks.

A breadth type: ``derivable`` True, so the scaled build draws more power banks from these rows by
the values their titles show (a form, a feature, a charging link, or a form and a link). The
body is the SKU's color. ``power_bank_form`` draws a slim brick, a rugged one with corner bumpers
or a magnetic one with a metal ring, and ``power_bank_charging`` draws a USB-C port and cable or
charge waves (:func:`kit_gadgets.power_bank`). Four title patterns, each by two brands. The four
``Charger`` rows of ``electronics_rows.py`` that are power banks stay chargers for a named device.
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
    QUORRIN,
    TORVANE,
    WEXMOOR,
)
from synthetic_ecommerce_data.domains.retail.gadgets_rows import (
    BLACK,
    POWER_BANKS,
    WHITE,
    decoy,
    row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

DEPARTMENT = "Electronics"


def _pb(code: str, title: str, brand: str, price: float, description: str, form: str,
        charging: str, feature: str) -> object:  # fmt: skip
    attrs = (a("power_bank_form", "Power bank form", form),
             a("power_bank_charging", "Power bank charging", charging),
             a("power_bank_feature", "Power bank feature", feature))  # fmt: skip
    return row(code, title, brand, POWER_BANKS, "Power Bank", "power_bank", price, description,
               attrs, (("power_bank_form", form.lower()), ("power_bank_charging", charging.lower())))  # fmt: skip


ROWS = (
    _pb("PWB001", "Slim Power Bank", WEXMOOR, 25.0,
        "Thin enough for a back pocket, with two full phone charges inside.", "Slim", "USB-C", "Kickstand"),
    _pb("PWB002", "Rugged Power Bank", BOLTWICK, 45.0,
        "Rubber corner bumpers and a sealed port cover for hikes and building sites.", "Rugged", "USB-C", "Built-in Cable"),
    _pb("PWB003", "Wireless Power Bank", TORVANE, 39.0,
        "Lay a phone on its face to charge it, no cable needed.", "Magnetic", "Wireless", "Kickstand"),
    _pb("PWB004", "USB-C Power Bank", DASKEL, 29.0,
        "One USB-C port that charges a phone, a tablet or a small laptop.", "Slim", "USB-C", "Built-in Cable"),
    _pb("PWB005", "Power Bank with Built-in Cable", QUORRIN, 35.0,
        "A short cable tucks into its side, so there is nothing to forget at home.", "Slim", "USB-C", "Built-in Cable"),
    _pb("PWB006", "Power Bank with Kickstand", NIMBREL, 42.0,
        "A fold-out stand holds the phone upright for a video call while it charges.", "Magnetic", "Wireless", "Kickstand"),
    _pb("PWB007", "Magnetic Wireless Power Bank", ARDMOOR, 49.0,
        "Snaps to the back of a phone and charges it while you keep using it.", "Magnetic", "Wireless", "Kickstand"),
    _pb("PWB008", "Rugged USB-C Power Bank", MERVANE, 55.0,
        "A drop-tested shell and a bright torch for camping trips and power cuts.", "Rugged", "USB-C", "Kickstand"),
)  # fmt: skip

SPEC = TypeSpec(
    key="power_bank",
    department=DEPARTMENT,
    product_type="Power Bank",
    derivable=True,
    owners=ELECTRONICS_OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "red power bank", "vocabulary", decoy(ROWS[0], "PWBRDL", "Slim Power Bank with Red Charge Lights",
              "A black slim power bank whose four charge lights glow red when it is low.", BLACK)),
        Decoy(6, "green power bank", "generic", decoy(ROWS[3], "PWBGHL", "Green Hollow USB-C Power Bank",
              "From the Green Hollow range: a USB-C power bank in white.", WHITE)),
    ),
)  # fmt: skip
