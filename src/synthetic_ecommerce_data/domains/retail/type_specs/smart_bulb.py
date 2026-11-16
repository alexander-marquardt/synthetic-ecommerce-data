"""Smart bulbs (gen#956): Electronics > Smart Home > Smart Bulbs.

A breadth type: ``derivable`` True. A product is its brand, range, ``bulb_shape`` and
``bulb_fitting`` (the 2026-11-15 ruling on gen#1005: every different product has a different
picture), and its title shows those two values alone, so the scaled build draws a new product for
each shape and fitting a brand does not sell yet, and only on a fitting the shape is sold on
(:data:`smart_home_rows.BULB_FITTINGS`). Each shape is drawn by its own outline
(:func:`kit_smart_home.smart_bulb`). The light (warm white, tunable white or color changing), the
connection and the brightness are the options of the SKUs, each in a single bulb, a 2 pack and a
4 pack, each priced on its own (:func:`smart_home_rows.bulb_skus`). Matter, the voice assistants it
works with and whether it needs a hub are filter-only attributes. The bulb is sold in white
frosted glass, its light color set in the app, so it is a main-color exception
(``main_colors.EXCEPTIONS``). Every template has its own brand and one title pattern, so a brand
sells one product of each shape and fitting. The two decoys carry brands the bulb templates do not
use, so neither draws its base row's brand and picture a second time.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.electronics_rows import (
    ARDMOOR,
    BOLTWICK,
    CINDREL,
    DASKEL,
    DUNVALE,
    ELECTRONICS_OWNERS,
    HALVERN,
    MARRICK,
    MERVANE,
    NIMBREL,
    PELLIMAR,
    QUORRIN,
    TORVANE,
    WEXMOOR,
    XELL,
)
from synthetic_ecommerce_data.domains.retail.smart_home_rows import WHITE, bulb_row, decoy
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Option, TypeSpec, a

DEPARTMENT = "Electronics"
CC, TW, WW = "Color Changing", "Tunable White", "Warm White"
WIFI, BT, ZB = "Wi-Fi", "Bluetooth", "Zigbee"


def _sb(code: str, brand: str, shape: str, fitting: str, description: str,
        variants: tuple[tuple[str, str, int], ...], matter: bool, assistants: tuple[str, ...]) -> object:  # fmt: skip
    """A bulb template: ``variants`` are its (light, connection, brightness step) SKU options."""
    hub = any(link == ZB for _, link, _ in variants)
    attrs = (a("matter", "Matter", "Yes" if matter else "No"),
             *(a("works_with", "Works with", w) for w in assistants),
             a("hub_required", "Hub required", "Yes" if hub else "No"))  # fmt: skip
    return bulb_row(code, brand, shape, fitting, description, variants, attrs)


_ALL = ("Alexa", "Google Home", "Apple Home")
ROWS = (
    _sb("SMB001", DASKEL, "A60 Standard", "E27",
        "Dims from the app or by voice, and joins a room scene with the other lights in the house.", ((CC, WIFI, 2), (TW, WIFI, 1)), True, _ALL),
    _sb("SMB002", MARRICK, "A60 Standard", "B22",
        "Set up from a phone in a minute, then dimmed from the app or a voice speaker.", ((WW, BT, 0), (TW, BT, 1)), False, ("Alexa", "Google Home")),
    _sb("SMB003", CINDREL, "Spot", "GU10",
        "A dimmable bulb for a kitchen ceiling, switched by voice or from the app.", ((WW, ZB, 0), (CC, ZB, 0)), True, _ALL),
    _sb("SMB004", PELLIMAR, "Candle", "E14",
        "A small bulb for a bedside lamp, with scenes for films and parties.", ((CC, BT, 0), (WW, BT, 0)), False, ("Alexa",)),
    _sb("SMB005", HALVERN, "Large Globe", "B22",
        "A statement bulb for a bare pendant, dimmed from the sofa with a phone.", ((WW, WIFI, 0), (CC, WIFI, 1)), True, ("Alexa", "Google Home")),
    _sb("SMB006", QUORRIN, "Golf Ball", "E14",
        "A neat bulb for a wall light or a small shade, grouped with the room in the app.", ((TW, ZB, 0), (CC, ZB, 0)), True, _ALL),
    _sb("SMB007", WEXMOOR, "Reflector", "E27",
        "Bright enough for a reading corner, and dimmed from the app or by voice.", ((TW, ZB, 1), (WW, ZB, 0)), False, ("Google Home",)),
    _sb("SMB008", TORVANE, "Edison Filament", "E27",
        "A glowing bulb for a cafe-style pendant, controlled from the app.", ((WW, BT, 0), (WW, WIFI, 1)), False, ("Alexa", "Google Home")),
    _sb("SMB009", NIMBREL, "Candle", "E27",
        "Lights a chandelier or a wall bracket, and dims with the rest of the room.", ((WW, WIFI, 0), (TW, WIFI, 0)), True, ("Alexa", "Apple Home")),
    _sb("SMB010", BOLTWICK, "Golf Ball", "E27",
        "Fits a small lampshade or a wall bracket, and dims from the app.", ((WW, ZB, 0), (TW, ZB, 0)), False, ("Alexa",)),
    _sb("SMB011", MERVANE, "Large Globe", "E27",
        "A big bulb that hangs bare from a pendant cord and fills a room with even light.", ((TW, WIFI, 0), (CC, WIFI, 1)), True, _ALL),
    _sb("SMB012", ARDMOOR, "Edison Filament", "B22",
        "Gives a hallway or a porch light a soft glow, switched from the app or a voice speaker.", ((WW, WIFI, 0), (WW, BT, 1)), False, ("Google Home",)),
)  # fmt: skip

SPEC = TypeSpec(
    key="smart_bulb",
    department=DEPARTMENT,
    product_type="Smart Bulb",
    derivable=True,
    owners=ELECTRONICS_OWNERS,
    options=(
        Option("bulb_light", "bulb_light", "Light"),
        Option("connectivity", "connectivity", "Connectivity"),
        Option("brightness_lm", "brightness", "Brightness (lm)"),
    ),
    rows=ROWS,
    decoys=(
        Decoy(4, "green smart bulb", "vocabulary", decoy(ROWS[1], "SMBGEN", "Green Energy A60 Standard Smart Bulb, B22 Fitting",
              "A white bulb that draws nine watts: its green energy label is its low power use.", WHITE, DUNVALE)),
        Decoy(6, "blue smart bulb", "generic", decoy(ROWS[2], "SMBBMW", "Blue Meadow Spot Smart Bulb, GU10 Fitting",
              "From the Blue Meadow range: a white smart bulb for a kitchen ceiling.", WHITE, XELL)),
    ),
)  # fmt: skip
