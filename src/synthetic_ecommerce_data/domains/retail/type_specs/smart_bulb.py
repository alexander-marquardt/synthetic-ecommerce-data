"""Smart bulbs (gen#956): Electronics > Smart Home > Smart Bulbs.

A breadth type: ``derivable`` True, so the scaled build draws more bulbs from these rows by the
values their titles show (fitting, light and connection). A smart bulb is sold in white frosted
glass, its light color set in the app, so it is a main-color exception
(``main_colors.EXCEPTIONS``); its SKUs are packs, a single bulb, a 2, 4 or 6 pack.
``bulb_fitting`` draws a screw base (E27, or the small E14), a bayonet base (B22) or a spot
on two pins (GU10) (:func:`kit_smart_home.smart_bulb`), with the key and name the lighting rows
use. Four title patterns, each by two brands.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    CINDREL,
    DASKEL,
    ELECTRONICS_OWNERS,
    HALVERN,
    MARRICK,
    PELLIMAR,
    QUORRIN,
    TORVANE,
    WEXMOOR,
)
from synthetic_ecommerce_data.domains.retail.smart_home_rows import BULBS, WHITE, decoy, row
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

DEPARTMENT = "Electronics"


def _sb(code: str, title: str, brand: str, price: float, description: str, fitting: str,
        light: str, link: str) -> object:  # fmt: skip
    attrs = (a("bulb_fitting", "Bulb fitting", fitting), a("bulb_light", "Light", light),
             a("connectivity", "Connectivity", link))  # fmt: skip
    packs = (("Single", price), ("2 pack", round(price * 1.8, 2)), ("4 pack", round(price * 3.4, 2)),
             ("6 pack", round(price * 4.8, 2)))  # fmt: skip
    return row(code, title, brand, BULBS, "Smart Bulb", "smart_bulb", price, description, attrs,
               (("bulb_fitting", fitting.lower()),), packs, "pack_size", (WHITE,))  # fmt: skip


ROWS = (
    _sb("SMB001", "E27 Color Changing Wi-Fi Smart Bulb", DASKEL, 15.0,
        "Sixteen million shades and a sunrise alarm, set from the app.", "E27", "Color Changing", "Wi-Fi"),
    _sb("SMB002", "B22 Tunable White Bluetooth Smart Bulb", MARRICK, 12.0,
        "Cool daylight for work and a warm glow for the evening, with no hub.", "B22", "Tunable White", "Bluetooth"),
    _sb("SMB003", "GU10 Warm White Smart Bulb", CINDREL, 9.0,
        "A dimmable spot for a kitchen ceiling, switched by voice or on a timer.", "GU10", "Warm White", "Zigbee"),
    _sb("SMB004", "E14 Color Changing Smart Bulb", PELLIMAR, 14.0,
        "A small candle bulb for a bedside lamp, with scenes for films and parties.", "E14", "Color Changing", "Bluetooth"),
    _sb("SMB005", "Wi-Fi Smart Bulb, B22 Fitting", HALVERN, 11.0,
        "Switch the hall light from the sofa or set it to come on at dusk.", "B22", "Warm White", "Wi-Fi"),
    _sb("SMB006", "Zigbee Smart Bulb, E14 Fitting", QUORRIN, 10.0,
        "A candle bulb that joins a smart hub and dims with the rest of the room.", "E14", "Tunable White", "Zigbee"),
    _sb("SMB007", "Dimmable Tunable White Zigbee Smart Bulb", WEXMOOR, 13.0,
        "A light that follows the day, from bright morning white to warm night.", "GU10", "Tunable White", "Zigbee"),
    _sb("SMB008", "Dimmable Warm White Bluetooth Smart Bulb", TORVANE, 8.0,
        "A soft glow that fades out at bedtime, paired with a phone in a minute.", "E27", "Warm White", "Bluetooth"),
)  # fmt: skip

SPEC = TypeSpec(
    key="smart_bulb",
    department=DEPARTMENT,
    product_type="Smart Bulb",
    derivable=True,
    owners=ELECTRONICS_OWNERS,
    rows=ROWS,
    decoys=(
        Decoy(4, "green smart bulb", "vocabulary", decoy(ROWS[1], "SMBGEN", "Green Energy B22 Tunable White Bluetooth Smart Bulb",
              "A white bulb that draws nine watts: its green energy label is its low power use.", WHITE)),
        Decoy(6, "blue smart bulb", "generic", decoy(ROWS[2], "SMBBMW", "Blue Meadow GU10 Warm White Smart Bulb",
              "From the Blue Meadow range: a warm white smart spot bulb.", WHITE)),
    ),
)  # fmt: skip
